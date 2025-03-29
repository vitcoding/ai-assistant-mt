import ollama

from core.logger import log
from db.vector_db import get_vector_db_client


async def get_docs(
    input_message: str,
    chroma_collection_name: str,
    embedding_model_name: str,
    embedding_search_results: int,
) -> list[str]:
    """Gets relevant docs for retrieved context."""

    vector_db_client = await get_vector_db_client()
    collection = await vector_db_client.get_or_create_collection(
        chroma_collection_name
    )
    queryembed = ollama.embeddings(
        model=embedding_model_name,
        prompt=input_message,
    )["embedding"]

    relevant_docs_data = await collection.query(
        query_embeddings=[queryembed],
        n_results=embedding_search_results,
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
