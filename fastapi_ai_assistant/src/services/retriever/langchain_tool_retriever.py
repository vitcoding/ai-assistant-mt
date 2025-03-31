import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.documents.base import Document
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings

from core.config import config
from core.logger import log

EMBEDDING_MODEL_NAME = config.llm.embedding_model
CHROMA_COLLECTION_NAME = "films_mt"
EMBEDDING_SEARCH_RESULTS = 5


embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL_NAME,
    base_url="http://localhost:11434",
)

chroma_settings = Settings(
    chroma_server_host="localhost",
    chroma_server_http_port=8010,
    anonymized_telemetry=False,
)

chroma = chromadb.HttpClient(
    host=config.vector_db.host,
    port=config.vector_db.port,
)

vector_store = Chroma(
    collection_name=CHROMA_COLLECTION_NAME,
    embedding_function=embeddings,
    client=chroma,
    # client_settings=chroma_settings,
)


@tool(response_format="content_and_artifact")
async def retrieve(query: str) -> tuple[str, list[Document]]:
    """Retrieves information related to a query."""

    log.info(f"{__name__}: query: \n{query}")

    retrieved_docs = await vector_store.asimilarity_search(
        query, k=EMBEDDING_SEARCH_RESULTS
    )

    serialized = "\n\n".join(
        (
            f"The retrieved document {data[0]}:"
            f"\nSource: {data[1].metadata["source"]}"
            f"\nContent: {data[1].page_content}"
        )
        for data in zip(range(1, len(retrieved_docs) + 1), retrieved_docs)
    )

    # log.debug(f"{__name__}: relevant_docs_data: \n{retrieved_docs}\n")
    log.debug(f"{__name__}: relevant_docs_data: \n{serialized}\n")

    return serialized, retrieved_docs
