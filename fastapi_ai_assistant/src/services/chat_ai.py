import json
from datetime import datetime, timezone
from json.decoder import JSONDecodeError
from typing import Any, AsyncGenerator, Sequence

from fastapi import WebSocket
from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    trim_messages,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated, TypedDict

from core.config import config
from core.logger import log
from prompts.chat_ai_templates import prompt_template
from prompts.rag_decision import get_prompt_decision
from services.audio.text_to_speech.en_tts import TextToSpeechEn
from services.audio.text_to_speech.ru_tts import TextToSpeechRu
from services.audio.text_to_speech.tts_speak import speak
from services.retriever.langchain_tool_retriever import retrieve
from services.retriever.ollama_retriever import get_docs
from services.tools.message_template import get_message_header
from services.tools.path_manager import PathManager

# LLM
PROVIDER = config.llm.provider
MODEL_KWARGS = {
    "keep_alive": 300,
    "max_new_tokens": 1_000,
    "temperature": 0.3,
    "repetition_penalty": 1.2,
}
MAIN_MODEL_KWARGS = MODEL_KWARGS
ANALYTICAL_MODEL_KWARGS = MODEL_KWARGS

ANALYTICAL_MODEL_NAME = config.llm.analytical_model

# Chat config params
CHAT_MAX_TOKENS = 10_000


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str
    docs_content: str


class ChatAI:
    """A class for work with AI chat."""

    def __init__(
        self,
        websocket: WebSocket,
        chat_id: str,
        chat_topic: str,
        model_name: str,
        language: str,
        use_rag: bool,
        use_sound: bool,
        path_manager: PathManager,
    ) -> None:
        self.websocket = websocket
        self.chat_id = chat_id
        self.chat_topic = chat_topic
        self.main_model_name = model_name
        self.language = language
        self.use_rag = use_rag
        self.use_sound = use_sound
        self.path_manager = path_manager
        self.retriever = "langchain_tool"
        # self.retriever = "ollama"
        self.speaker = None
        self.user_role_name = self._get_user_role_name()
        self.ai_role_name = self._get_ai_role_name()
        self.chat_timestamp = datetime.now(timezone.utc).isoformat()
        self.analytical_model_name = ANALYTICAL_MODEL_NAME
        self.llm_analytical = init_chat_model(
            model=self.analytical_model_name,
            model_provider=PROVIDER,
            **ANALYTICAL_MODEL_KWARGS,
        )
        self.llm_main = init_chat_model(
            model=self.main_model_name,
            model_provider=PROVIDER,
            **MAIN_MODEL_KWARGS,
        )
        self.trimmer = trim_messages(
            max_tokens=CHAT_MAX_TOKENS,
            strategy="last",
            token_counter=self.llm_analytical,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )
        self.graph_builder = StateGraph(state_schema=State)
        self.memory = MemorySaver()
        self.tools = ToolNode([retrieve])
        self.chat_config = {"configurable": {"thread_id": self.chat_id}}
        self.graph = self._set_workflow()
        self.ai_audio_file_name = None

    def _tools_condition(self, state: State) -> str:
        """Sets tools conditions."""

        last_message = state["messages"][-1]

        if getattr(last_message, "rag_required", True) == False:
            return "generate"
        elif hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "tools"

    def _set_workflow(self) -> StateGraph:
        """The chat workfow settings."""

        log.debug(f"{__name__}: {self._set_workflow.__name__}: start")

        log.info(
            f"{__name__}: {self._set_workflow.__name__}: "
            f"\nmodel setted: {self.main_model_name}"
        )
        log.info(
            f"{__name__}: {self._set_workflow.__name__}: "
            f"\nanswer languge setted: {self.language}"
        )
        log.info(
            f"{__name__}: {self._set_workflow.__name__}: "
            f"\nuse_rag setted: {self.use_rag}"
        )

        if not self.use_sound:
            self.speaker = None
        elif self.language == "Russian":
            self.speaker = TextToSpeechRu()
        elif self.language == "English":
            self.speaker = TextToSpeechEn()

        if self.use_rag and self.retriever == "langchain_tool":
            self.graph_builder.add_node(
                "query_or_respond", self._query_or_respond
            )
            self.graph_builder.add_node("tools", self.tools)
            self.graph_builder.add_node("generate", self._generate)

            self.graph_builder.set_entry_point("query_or_respond")
            self.graph_builder.add_conditional_edges(
                "query_or_respond",
                self._tools_condition,
                {END: END, "tools": "tools", "generate": "generate"},
            )
            self.graph_builder.add_edge("tools", "generate")
            self.graph_builder.add_edge("generate", END)

            graph = self.graph_builder.compile(checkpointer=self.memory)
            log.debug(f"{__name__}: {self._set_workflow.__name__}: end")
            return graph

        self.graph_builder.add_edge(START, "generate")
        self.graph_builder.add_node("generate", self._generate)
        graph = self.graph_builder.compile(checkpointer=self.memory)
        log.debug(f"{__name__}: {self._set_workflow.__name__}: end")
        return graph

    def _get_user_role_name(self) -> str:
        """Gets the user role name."""

        user_role_names = {"Russian": "Я", "English": "Me"}
        user_role_name = (
            user_role_names[self.language]
            if self.language in user_role_names
            else user_role_names["English"]
        )
        return user_role_name

    def _get_ai_role_name(self) -> str:
        """Gets the ai role name."""

        ai_role_names = {"Russian": "ИИ", "English": "AI"}
        ai_role_name = (
            ai_role_names[self.language]
            if self.language in ai_role_names
            else ai_role_names["English"]
        )
        return ai_role_name

    async def _query_or_respond(self, state: State):
        """Generate tool call for retrieval or respond."""

        prompt_decision = get_prompt_decision(state["messages"][-1].content)

        log.debug(
            f"{__name__}: {self._query_or_respond.__name__}: "
            f"\nprompt_decision: \n{prompt_decision}\n"
        )

        response = await self.llm_analytical.ainvoke(prompt_decision)
        log.debug(
            f"{__name__}: {self._query_or_respond.__name__}: "
            f"\nresponse (prompt_decision): \n{response}\n"
        )
        try:
            decision = json.loads(response.content)
        except JSONDecodeError as err:
            log.error(
                f"{__name__}: {self._query_or_respond.__name__}: "
                f"\nAn error '{type(err)}': {err}\n"
            )
            decision = {"rag_decision": False}

        log.info(
            f"{__name__}: {self._query_or_respond.__name__}: "
            f"\nRAG decision: {decision}\n"
        )

        if decision["rag_decision"]:
            llm_with_tools = self.llm_analytical.bind_tools([retrieve])
            response = await llm_with_tools.ainvoke(state["messages"])
            return {"messages": response}
        else:
            return {"messages": [AIMessage(content="", rag_required=False)]}

    async def _generate(self, state: State) -> dict[str, Any]:
        """Provides model call."""

        trimmed_messages = await self.trimmer.ainvoke(state["messages"])

        # trimmed_messages
        trimmed_messages_str = "\n\n".join(
            [repr(message) for message in trimmed_messages]
        )
        log.debug(
            f"{__name__}: {self._generate.__name__}: "
            f"\ntrimmed_messages: \n{trimmed_messages_str}\n"
        )

        # docs_content
        docs_system_message = (
            "\n\n\nCheck the information in the retrieved documents from the retrieved context. If this information corresponds to the user's request, then rely on it when responding."
            "\n\nRetrieved context:\n\n"
        )

        if self.use_rag and self.retriever == "langchain_tool":
            retrieved_docs = trimmed_messages[-1].content
            docs_content = f"{docs_system_message}{retrieved_docs}"
        elif self.use_rag and self.retriever == "ollama":
            docs_list = await get_docs(
                trimmed_messages[-1].content,
            )
            docs_content = ""
            if isinstance(docs_list, (list, tuple)):
                docs_text = "\n\n".join(doc for doc in docs_list)
                docs_content = f"{docs_system_message}{docs_text}"
        else:
            docs_content = ""
        # log.debug(
        #     f"{__name__}: {self._generate.__name__}: "
        #     f"\ndocs_content: \n{docs_content}\n"
        # )

        trimmed_messages_filtered = []
        for message in trimmed_messages:
            if isinstance(message, HumanMessage) or (
                isinstance(message, AIMessage) and message.content
            ):
                trimmed_messages_filtered.append(message)

        trimmed_messages_filtered_str = "\n\n".join(
            [repr(message) for message in trimmed_messages_filtered]
        )

        log.debug(
            f"{__name__}: {self._generate.__name__}: "
            f"\ntrimmed_messages_filtered: \n{trimmed_messages_filtered_str}\n"
        )

        prompt = await prompt_template.ainvoke(
            {
                "messages": trimmed_messages_filtered,
                "language": state["language"],
                "docs_content": docs_content,
            }
        )

        prompt_str = "\n\n".join(
            [
                f">>>\n{message.type}: {message.content}"
                for message in prompt.messages
            ]
            # [repr(message) for message in prompt.messages]
        )
        prompt_str = f"{'-'*30}\n{prompt_str}\n{'-'*30}\n"
        log.info(
            f"{__name__}: {self._generate.__name__}: "
            f"\nprompt: \n{prompt_str}\n"
        )

        response = await self.llm_main.ainvoke(prompt)
        return {"messages": response}

    async def send_message(
        self, message: str, role: str | None = None
    ) -> None:
        """Sends a message to the chat."""

        message_header, _ = get_message_header(self.language, role)
        await self.websocket.send_text(f"{message_header} \n{message}")
        await self.websocket.send_text("<<<end>>>")
        log.info(
            f"{__name__}: {self.process.__name__}: chat message:"
            f"\n{role}: \n'''\n{message}\n'''"
        )

    async def process(
        self, input_message: str, ai_file_name: str
    ) -> AsyncGenerator:
        """Processes user messages."""

        log.debug(f"{__name__}: {self.process.__name__}: start")

        if not input_message.strip():
            response_no_input = {
                "Russian": "Вы ничего не ввели, "
                + "скажите или напишите что-нибудь.",
                "English": "You haven't entered anything, "
                + "tell or write something.",
            }
            system_message = (
                response_no_input[self.language]
                if self.language in response_no_input
                else response_no_input["English"]
            )
            yield system_message
            if self.speaker:
                file_path = (
                    f"{self.path_manager.chat_dir_audio}{ai_file_name}.wav"
                )
                await speak(self.speaker, system_message, file_path)
            yield "<<<end>>>"

            log.debug(f"{__name__}: {self.process.__name__}: end (no input)")
        else:
            # stream
            message_list = []
            async for chunk_data in self.graph.astream(
                {
                    "messages": HumanMessage(input_message),
                    "language": self.language,
                    "docs_content": "",
                    # "docs_content": docs_content,
                },
                stream_mode="messages",
                config=self.chat_config,
            ):
                if (
                    chunk_data[0].type == "AIMessageChunk"
                    and not chunk_data[0].tool_calls
                    # and chunk_data[0].content
                    and chunk_data[1]["langgraph_node"] != "query_or_respond"
                ):
                    message_chunk = chunk_data[0].content
                    message_list.append(message_chunk)
                    yield message_chunk

            ai_message = "".join(message_list) if message_list else ""

            if self.speaker:
                file_path = (
                    f"{self.path_manager.chat_dir_audio}{ai_file_name}.wav"
                )
                try:
                    await speak(self.speaker, ai_message, file_path)
                    await self.websocket.send_text(
                        f"<<<ai_file_name>>> {self.ai_audio_file_name}"
                    )
                except Exception as err:
                    log.error(
                        f"{__name__}: {self.process.__name__}: "
                        f"\nError {type(err)}: {err}"
                    )
                    self.ai_audio_file_name = None

            yield "<<<end>>>"

            log.info(
                f"{__name__}: {self.process.__name__}: chat message:"
                f"\n{self.ai_role_name} \n'''\n{ai_message}\n'''"
            )

            log.debug(f"{__name__}: {self.process.__name__}: end")
