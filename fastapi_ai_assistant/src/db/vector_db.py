import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from core.config import config
from core.logger import log

EMBEDDING_MODEL_NAME = config.llm.embedding_model
CHROMA_COLLECTION_NAME = "example_langchain"

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)


async def get_vector_db_client():
    client = await chromadb.AsyncHttpClient(
        host=config.vector_db.host,
        port=config.vector_db.port,
    )
    return client
