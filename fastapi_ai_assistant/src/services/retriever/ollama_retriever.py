import ollama

from core.config import config
from core.logger import log
from db.vector_db import get_vector_db_client

EMBEDDING_MODEL_NAME = config.llm.embedding_model
CHROMA_COLLECTION_NAME = "films_mt"
EMBEDDING_SEARCH_RESULTS = 5


async def get_docs(
    input_message: str,
) -> list[str]:
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
        for data in zip(range(1, len(sources) + 1), sources, retrieved_docs)
    ]
    relevant_docs = [
        f"The retrieved document {data[0]}:\nSource: '{data[1]}'\n"
        f"The context of the document:\n'{data[2]}'"
        for data in retrieved_data
    ]
    return relevant_docs
