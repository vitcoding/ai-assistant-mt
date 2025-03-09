import chromadb
from langchain_ollama import OllamaEmbeddings

from core.config import config

EMBEDDING_MODEL_NAME = config.llm.embedding_model

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)


async def get_vector_db_client():
    """Gets a vector db client."""

    client = await chromadb.AsyncHttpClient(
        host=config.vector_db.host,
        port=config.vector_db.port,
    )
    return client
