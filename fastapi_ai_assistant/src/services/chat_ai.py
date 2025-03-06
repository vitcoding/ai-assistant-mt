from datetime import datetime, timezone
from typing import Sequence

import ollama
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
from db.vector_db import get_vector_db_client

EMBEDDING_MODEL_NAME = config.llm.embedding_model
CHROMA_COLLECTION_NAME = "example_langchain"

# LLM
MODEL_NAME = config.llm.model
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
    def __init__(self, chat_id, language="Russian"):
        self.language = language
        self.chat_start_timestamp = datetime.now(timezone.utc).isoformat()
        self.llm = init_chat_model(
            model=MODEL_NAME, model_provider=PROVIDER, **MODEL_KWARGS
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
        self.chat_config = {"configurable": {"thread_id": chat_id}}
        self.graph = self._set_workflow()

    def _set_workflow(self):
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

    async def get_docs(self, input_message):
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
        # log.debug(f"{__name__}: relevant_docs: \n\n{relevant_docs}")
        return relevant_docs

    async def process(self, input_message):
        log.info(f"{__name__}: {self.process.__name__}: start")

        if not input_message:
            log.info(f"{__name__}: {self.process.__name__}: end (no input)")
            return "?"

        # docs content
        docs = await self.get_docs(input_message)
        if isinstance(docs, (list, tuple)):
            docs_content = "\n\n".join(doc for doc in docs)
        else:
            docs_content = ""
        log.info(f"{__name__}: docs_content: \n{docs_content}")

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

            log.info(
                f"{__name__}: {self.process.__name__}: "
                f"\nStep {step_type}: \ncontent:\n'''\n{content}\n'''"
            )
            log.debug(
                f"{__name__}: {self.process.__name__}: "
                f"\nstep_message: \n{last_step}"
            )

        log.info(f"{__name__}: {self.process.__name__}: end")
        return content
