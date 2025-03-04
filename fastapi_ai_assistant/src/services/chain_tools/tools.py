from langchain_core.tools import tool

from core.logger import log
from db.vector_db import get_vector_store


@tool(response_format="content_and_artifact")
async def retrieve(query: str):
    """Retrieves information related to a query."""

    log.info(f"{__name__}: retrieve: start")

    vector_store = get_vector_store()

    retrieved_docs = await vector_store.asimilarity_search(query, k=2)

    log.debug(f"{__name__}: retrieved_docs: \n{retrieved_docs}")

    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    log.info(f"{__name__}: retrieve: end")
    return serialized, retrieved_docs
