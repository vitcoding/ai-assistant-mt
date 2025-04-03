import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from core.config import config

EMBEDDING_MODEL_NAME = config.llm.embedding_model


embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL_NAME,
    base_url=f"http://{config.llm.host}:{config.llm.port}",
)


def get_vector_store(chroma_collection_name: str) -> Chroma:
    """Gets a vector store."""

    chroma_settings = Settings(
        chroma_server_host=config.vector_db.host,
        chroma_server_http_port=config.vector_db.port,
        anonymized_telemetry=False,
    )
    chroma = chromadb.HttpClient(
        host=config.vector_db.host,
        port=config.vector_db.port,
    )

    vector_store = Chroma(
        collection_name=chroma_collection_name,
        embedding_function=embeddings,
        client=chroma,
        # client_settings=chroma_settings,
    )
    return vector_store


async def get_vector_db_client():
    """Gets a vector db client."""

    client = await chromadb.AsyncHttpClient(
        host=config.vector_db.host,
        port=config.vector_db.port,
    )
    return client
