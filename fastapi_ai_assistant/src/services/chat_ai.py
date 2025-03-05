from datetime import datetime, timezone
from typing import Sequence

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from core.config import config
from core.logger import log

MODEL_NAME = config.llm.model
PROVIDER = config.llm.provider

EMBEDDING_MODEL_NAME = config.llm.embedding_model

MODEL_KWARGS = {
    "keep_alive": 300,
    "max_new_tokens": 100,
    "temperature": 0.3,
    "repetition_penalty": 1.2,
}

prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            "You are a helpful assistant named 'AI Chat'. Answer all questions "
            "to the best of your ability in {language}."
            "{docs_content}",
        ),
        # (
        #     "You are an assistant for question-answering tasks. "
        #     "Use the following pieces of retrieved context to answer "
        #     "the question. If you don't know the answer, say that you "
        #     "don't know. Use three sentences maximum and keep the "
        #     "answer concise."
        #     "You must speak only {language}."
        #     "\n\n"
        #     "{docs_content}"
        # ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str
    docs_content: str


class ChatAI:
    def __init__(self, chat_id, language="Russian"):
        self.language = language
        self.chat_start_timestamp = datetime.now(timezone.utc).isoformat()
        self.llm = init_chat_model(
            model=MODEL_NAME, model_provider=PROVIDER, **MODEL_KWARGS
        )
        self.trimmer = trim_messages(
            max_tokens=10_000,
            strategy="last",
            token_counter=self.llm,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )
        self.graph_builder = StateGraph(state_schema=State)
        self.memory = MemorySaver()
        self.chat_config = {"configurable": {"thread_id": chat_id}}
        self.graph = self._set_workflow(chat_id)

    def _set_workflow(self, thread_id):
        log.info(f"{__name__}: {self._set_workflow.__name__}: start")

        self.graph_builder.add_edge(START, "model")
        self.graph_builder.add_node("model", self._call_model)

        graph = self.graph_builder.compile(checkpointer=self.memory)
        log.info(f"{__name__}: {self._set_workflow.__name__}: end")
        return graph

    async def _call_model(self, state: State):
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

    async def process(self, input_message):
        log.info(f"{__name__}: {self.process.__name__}: start")

        # docs content
        # docs_content = "\n\n".join(doc.content for doc in docs)
        docs_content = ""

        # stream
        async for step in self.graph.astream(
            {
                "messages": HumanMessage(input_message),
                "language": self.language,
                "docs_content": docs_content,
            },
            stream_mode="values",
            config=self.chat_config,
        ):
            step["messages"][-1].pretty_print()

            last_step = step["messages"][-1]
            content = getattr(last_step, "content")
            response_metadata = getattr(last_step, "response_metadata")
            if content and response_metadata:
                try:
                    model = response_metadata["model"]
                except KeyError:
                    model = "no info"
                    step_type = f"AI message ('model: {model}')"
            else:
                step_type = "User message"

            log.warning(
                f"{__name__}: {self.process.__name__}: "
                f"\nStep {step_type}: \ncontent:\n'''\n{content}\n'''"
            )
            log.debug(
                f"{__name__}: {self.process.__name__}: "
                f"\nstep_message: \n{last_step}"
            )

        log.info(f"{__name__}: {self.process.__name__}: end")
        return content
