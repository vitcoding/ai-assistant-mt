from dataclasses import dataclass

import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from pydantic import BaseModel

from core.logger import logger
from db.db import chroma_config, ollama_config


class FilmDoc(BaseModel):
    id: str
    page_content: str
    metadata: dict


class VectorDBLoader:
    """Класс для загрузки данных в векторную базу данных."""

    def __init__(
        self,
        collection_name: str = "films_mt",
        embedding_model_name: str = "evilfreelancer/enbeddrus",
    ):
        self.collection_name = collection_name
        self.embeddings = OllamaEmbeddings(
            model=embedding_model_name,
            base_url=f"http://{ollama_config.host}:{ollama_config.port}",
        )
        self.vector_store = self._get_vector_store()

    def _get_vector_store(self, clean_db: bool = False) -> Chroma:
        """Создает подключение к векторной базе данных."""

        chroma = chromadb.HttpClient(
            host=chroma_config.host, port=chroma_config.port
        )

        if clean_db:
            logger.debug(
                f"{__name__}: chroma.list_collections: "
                f"\n{chroma.list_collections()}"
            )
            if any(
                collection == self.collection_name
                for collection in chroma.list_collections()
            ):
                logger.debug(
                    f"{__name__}: deleting collection '{self.collection_name}'"
                )
                chroma.delete_collection(self.collection_name)

        collection = chroma.get_or_create_collection(self.collection_name)

        vector_store = Chroma(
            client=chroma,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )
        return vector_store

    def list_to_text(self, data: list):
        """Метод приведения итерируемых объектов к строковым."""
        if data:
            return ", ".join(data)
        return ""

    def transform_film_data(self, film_data: dict) -> dict:
        """Трансформирует словарь с данными о фильме."""

        film_info = {}
        for key, value in film_data.items():
            match key:
                case "imdb_rating":
                    film_info.update({key: str(value)})
                case "title":
                    film_info.update({key: str(value)})
                case "description":
                    film_info.update({key: str(value)})
                case (
                    "genres"
                    | "directors_names"
                    | "actors_names"
                    | "writers_names"
                ):
                    film_info.update({key: self.list_to_text(value)})
        logger.debug(f"{__name__}: film_info: " f"\n{film_info}")
        return film_info

    def get_film_context(self, film: dict) -> str:
        """Преобразует данные о фильме из словаря в текст."""

        title = film.get("title", "no data")
        imdb_rating = film.get("imdb_rating", "no data")
        description = film.get("description", "no data")
        genres = film.get("genres", "no data")
        directors_names = film.get("directors_names", "no data")
        actors_names = film.get("actors_names", "no data")
        writers_names = film.get("writers_names", "no data")
        film_text_data = (
            f"Film '{title}':\n"
            f"Rating: '{imdb_rating}'\n"
            f"Description: '{description}'\n"
            f"Genres: '{genres}'\n"
            f"Directors: '{directors_names}'\n"
            f"Actors: '{actors_names}'\n"
            f"Writers: '{writers_names}'"
        )
        logger.debug(f"{__name__}: film_text_data: " f"\n{film_text_data}")
        return film_text_data

    def load_vectors(self, films: list[dict]):
        """Загружает данные о фильме в векторную базу."""

        films_docs = []
        for film in films:
            transformed_film_dict = self.transform_film_data(film)
            film_context = self.get_film_context(transformed_film_dict)
            film_doc = {
                "id": str(film["id"]),
                "page_content": film_context,
                "metadata": {"source": "movie library"},
            }
            films_docs.append(film_doc)

        docs = [FilmDoc(**doc) for doc in films_docs]
        logger.debug(f"{__name__}: docs: " f"\n{docs}")
        if docs:
            self.vector_store.add_documents(docs)
