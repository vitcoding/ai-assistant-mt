from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Sequence

import ollama
from fastapi import WebSocket
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from core.config import config
from core.logger import log
from db.vector_db import get_vector_db_client
from services.audio.text_to_speech.en_tts import TextToSpeechEn
from services.audio.text_to_speech.ru_tts import TextToSpeechRu
from services.audio.text_to_speech.tts_speak import speak

EMBEDDING_MODEL_NAME = config.llm.embedding_model
CHROMA_COLLECTION_NAME = "films_mt"
# CHROMA_COLLECTION_NAME = "example_langchain"

# LLM
# MODEL_NAME = config.llm.model
PROVIDER = config.llm.provider
MODEL_KWARGS = {
    "keep_alive": 300,
    "max_new_tokens": 1_000,
    "temperature": 0.3,
    "repetition_penalty": 1.2,
}

# Embedding
EMBEDDING_MODEL_NAME = config.llm.embedding_model
EMBEDDING_SEARCH_RESULTS = 3

# Chat config params
CHAT_MAX_TOKENS = 10_000

prompt_template = ChatPromptTemplate.from_messages(
    [
        # SystemMessage(
        #     "You are a helpful assistant named 'AI Chat'. Answer all questions "
        #     "to the best of your ability in {language}."
        #     "{docs_content}",
        # ),
        (
            "system",
            "Your name is 'ИИ Ассистент'. "
            "You are an assistant for question-answering tasks. \n"
            "Use the retrieved documents of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise. "
            "You must speak only {language}."
            "\n\n\n"
            "Retrieved context:\n\n{docs_content}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


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
    ) -> None:
        self.websocket = websocket
        self.chat_id = chat_id
        self.chat_topic = chat_topic
        self.model_name = model_name
        self.language = language
        self.use_rag = use_rag
        self.use_sound = use_sound
        self.speaker = None
        self.user_role_name = self._get_user_role_name()
        self.ai_role_name = self._get_ai_role_name()
        self.chat_start_timestamp = datetime.now(timezone.utc).isoformat()
        self.llm = init_chat_model(
            model=self.model_name, model_provider=PROVIDER, **MODEL_KWARGS
        )
        self.trimmer = trim_messages(
            max_tokens=CHAT_MAX_TOKENS,
            strategy="last",
            token_counter=self.llm,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )
        self.graph_builder = StateGraph(state_schema=State)
        self.memory = MemorySaver()
        self.chat_config = {"configurable": {"thread_id": self.chat_id}}
        self.graph = self._set_workflow()

    def _set_workflow(self) -> StateGraph:
        """The chat workfow settings."""

        log.debug(f"{__name__}: {self._set_workflow.__name__}: start")

        log.info(
            f"{__name__}: {self._set_workflow.__name__}: "
            f"\nmodel setted: {self.model_name}"
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

        self.graph_builder.add_edge(START, "model")
        self.graph_builder.add_node("model", self._call_model)

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

    async def _call_model(self, state: State) -> dict[str, Any]:
        """Provides model call."""

        trimmed_messages = await self.trimmer.ainvoke(state["messages"])
        prompt = await prompt_template.ainvoke(
            {
                "messages": trimmed_messages,
                "language": state["language"],
                "docs_content": state["docs_content"],
            }
        )
        response = await self.llm.ainvoke(prompt)
        return {"messages": response}

    async def get_docs(self, input_message) -> list[str]:
        """Gets relevant docs for retrieved context."""

        vector_db_client = await get_vector_db_client()
        collection = await vector_db_client.get_or_create_collection(
            CHROMA_COLLECTION_NAME
        )
        queryembed = ollama.embeddings(
            model=EMBEDDING_MODEL_NAME,
            prompt=input_message,
        )["embedding"]

        relevant_docs_data = await collection.query(
            query_embeddings=[queryembed],
            n_results=EMBEDDING_SEARCH_RESULTS,
        )
        log.debug(f"{__name__}: relevant_docs_data: \n{relevant_docs_data}")

        metadatas = relevant_docs_data["metadatas"][0]
        sources = [metadata.get("source") for metadata in metadatas]
        retrieved_docs = relevant_docs_data["documents"][0]

        retrieved_data = [
            data
            for data in zip(
                range(1, len(sources) + 1), sources, retrieved_docs
            )
        ]
        relevant_docs = [
            f"The retrieved document {data[0]}:\nSource: '{data[1]}'\n"
            f"The context of the document:\n'{data[2]}'"
            for data in retrieved_data
        ]
        return relevant_docs

    async def send_message(self, role: str, message: str) -> None:
        """Sends a message to the chat."""

        timestamp = datetime.now().isoformat()
        await self.websocket.send_text(f"[{timestamp}] {role}: \n{message}")
        await self.websocket.send_text("<<<end>>>")
        log.info(
            f"{__name__}: {self.process.__name__}: chat message:"
            f"\n{role}: \n'''\n{message}\n'''"
        )

    async def process(self, input_message: str) -> AsyncGenerator:
        """Processes user messages."""

        log.debug(f"{__name__}: {self.process.__name__}: start")

        if not input_message:
            response_no_input = {
                "Russian": "Вы ничего не ввели, напишите что-нибудь.",
                "English": "You haven't entered anything, write something.",
            }
            system_message = (
                response_no_input[self.language]
                if self.language in response_no_input
                else response_no_input["English"]
            )
            yield system_message
            yield "<<<end>>>"

            log.debug(f"{__name__}: {self.process.__name__}: end (no input)")
        else:
            # docs content
            docs = ""
            if self.use_rag:
                docs = await self.get_docs(input_message)
            if isinstance(docs, (list, tuple)):
                docs_content = "\n\n".join(doc for doc in docs)
            else:
                docs_content = ""
            log.info(
                f"{__name__}: {self.process.__name__}: "
                f"\ndocs_content: \n{docs_content}"
            )

            # stream
            message_list = []
            async for chunc_data in self.graph.astream(
                {
                    "messages": HumanMessage(input_message),
                    "language": self.language,
                    "docs_content": docs_content,
                },
                stream_mode="messages",
                config=self.chat_config,
            ):
                message_chunk = chunc_data[0].content
                message_list.append(message_chunk)
                yield message_chunk

            ai_message = "".join(message_list) if message_list else ""

            if self.speaker:
                await speak(self.speaker, ai_message)

            yield "<<<end>>>"

            log.info(
                f"{__name__}: {self.process.__name__}: chat message:"
                f"\n{self.ai_role_name} \n'''\n{ai_message}\n'''"
            )

            log.debug(f"{__name__}: {self.process.__name__}: end")
