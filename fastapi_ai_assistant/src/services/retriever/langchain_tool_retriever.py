from langchain_core.documents.base import Document
from langchain_core.tools import tool

from core.logger import log
from db.vector_db import get_vector_store

CHROMA_COLLECTION_NAME = "films_mt"
EMBEDDING_SEARCH_RESULTS = 5


@tool(response_format="content_and_artifact")
async def retrieve(query: str) -> tuple[str, list[Document]]:
    """Retrieves information related to a query."""

    log.info(f"{__name__}: query: \n{query}")

    vector_store = get_vector_store(CHROMA_COLLECTION_NAME)
    retrieved_docs = await vector_store.asimilarity_search(
        query, k=EMBEDDING_SEARCH_RESULTS
    )

    serialized = "\n\n".join(
        (
            f"The retrieved document {data[0]}:"
            f"\nSource: {data[1].metadata['source']}"
            f"\nContent: {data[1].page_content}"
        )
        for data in zip(range(1, len(retrieved_docs) + 1), retrieved_docs)
    )

    # log.debug(f"{__name__}: relevant_docs_data: \n{retrieved_docs}\n")
    log.debug(f"{__name__}: relevant_docs_data: \n{serialized}\n")

    return serialized, retrieved_docs
