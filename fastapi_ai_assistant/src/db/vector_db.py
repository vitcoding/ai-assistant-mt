import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from core.config import config
from core.logger import log

EMBEDDING_MODEL_NAME = config.llm.embedding_model
CHROMA_COLLECTION_NAME = "example_langchain"

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)


def get_vector_store(
    collection_name: str = CHROMA_COLLECTION_NAME, clean_db: bool = False
):
    log.info(f"{__name__}: {get_vector_store.__name__}: start")
    chroma = chromadb.HttpClient(
        host=config.vector_db.host,
        port=config.vector_db.port,
    )

    if clean_db:
        log.info(
            f"{__name__}: chroma.list_collections: "
            f"\n{chroma.list_collections()}"
        )
        if any(
            collection == collection_name
            for collection in chroma.list_collections()
        ):
            log.info(f"{__name__}: deleting collection '{collection_name}'")
            chroma.delete_collection(collection_name)

    collection = chroma.get_or_create_collection(collection_name)

    vector_store = Chroma(
        client=chroma,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

    log.info(f"{__name__}: {get_vector_store.__name__}: end")

    return vector_store
