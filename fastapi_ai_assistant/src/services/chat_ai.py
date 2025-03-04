from datetime import datetime, timezone

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from core.config import config
from core.logger import log
from services.chain_tools.tools import retrieve

MODEL_NAME = config.llm.model
PROVIDER = config.llm.provider

EMBEDDING_MODEL_NAME = config.llm.embedding_model

MODEL_KWARGS = {
    "keep_alive": 300,
    "max_new_tokens": 100,
    "temperature": 0.3,
    "repetition_penalty": 1.2,
}


class ChatAI:
    def __init__(self, chat_id):
        self.llm = init_chat_model(
            model=MODEL_NAME, model_provider=PROVIDER, **MODEL_KWARGS
        )
        self.chat_start_timestamp = datetime.now(timezone.utc).isoformat()
        self.tools = ToolNode([retrieve])
        self.graph_builder = StateGraph(MessagesState)
        self.memory = MemorySaver()
        self.chat_config = {"configurable": {"thread_id": chat_id}}
        self.graph = self._set_chat(chat_id)

    def _set_chat(self, thread_id):
        log.info(f"{__name__}: {self._set_chat.__name__}: start")
        # await load_data()

        self.graph_builder.add_node(self.query_or_respond)
        self.graph_builder.add_node(self.tools)
        self.graph_builder.add_node(self.generate_response)

        self.graph_builder.set_entry_point("query_or_respond")
        self.graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        self.graph_builder.add_edge("tools", "generate_response")
        self.graph_builder.add_edge("generate_response", END)

        graph = self.graph_builder.compile(checkpointer=self.memory)
        log.info(f"{__name__}: {self._set_chat.__name__}: end")
        return graph

    async def query_or_respond(self, state: MessagesState):
        """Generates tool call for retrieval or respond."""

        log.info(f"{__name__}: {self.query_or_respond.__name__}: start")

        llm_with_tools = self.llm.bind_tools([retrieve])
        response = await llm_with_tools.ainvoke(state["messages"])
        # response = await self.llm.ainvoke(state["messages"])

        # MessagesState appends messages to state instead of overwriting
        log.info(f"{__name__}: {self.query_or_respond.__name__}: end")
        return {"messages": [response]}

    async def generate_response(self, state: MessagesState):
        """Generates answer."""

        log.info(f"{__name__}: {self.generate_response.__name__}: start")
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "You must speak only Russian."
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [
            SystemMessage(system_message_content)
        ] + conversation_messages

        # Run
        response = await self.llm.ainvoke(prompt)
        log.info(f"{__name__}: {self.generate_response.__name__}: end")
        return {"messages": [response]}

    async def process(self, input_message):
        log.info(f"{__name__}: {self.process.__name__}: start")

        # stream
        async for step in self.graph.astream(
            {"messages": [{"role": "user", "content": input_message}]},
            stream_mode="values",
            config=self.chat_config,
        ):
            step["messages"][-1].pretty_print()

            last_step = step["messages"][-1]
            content = getattr(last_step, "content")
            tool_name = getattr(last_step, "name")
            response_metadata = getattr(last_step, "response_metadata")
            if content and tool_name:
                step_type = f"Query response (tool name: '{tool_name}')"
            elif response_metadata:
                try:
                    model = response_metadata["model"]
                except KeyError:
                    model = "no info"

                if content:
                    step_type = f"AI message ('model: {model}')"
                else:
                    try:
                        query = last_step.tool_calls[0]["args"]["query"]
                    except KeyError:
                        query = "None"
                    step_type = f"AI query: \n'{query}'"
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
