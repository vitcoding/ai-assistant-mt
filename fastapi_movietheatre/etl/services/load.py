from dataclasses import dataclass
from typing import Dict, List, Union, ValuesView

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError

from core.config import BATCH_SIZE, PostgresRow, Schemas
from core.decorators import backoff
from core.logger import logger
from services.elasticsearch_index_definitions import INDEX, SETTINGS
from services.load_vector_db import VectorDBLoader


@dataclass
class ElasticLoader(object):
    elastic: Elasticsearch
    vector_loader: VectorDBLoader = VectorDBLoader()

    @backoff(errors=(ConnectionError,))
    def __post_init__(self):
        """
        Инициализирует ElasticLoader, создавая индексы в Elasticsearch, если они еще не существуют.
        """
        for index, properties in INDEX.items():
            if not self.elastic.indices.exists(index=index):
                body = {
                    "settings": SETTINGS,
                    "mappings": {
                        "dynamic": "strict",
                        "properties": properties,
                    },
                }
                self.elastic.indices.create(index=index, body=body)

    @backoff(errors=(ConnectionError,))
    def bulk_insert(
        self, schema: Schemas, data: Union[List[PostgresRow], ValuesView[Dict]]
    ):
        """
        Выполняет массовую вставку данных в Elasticsearch и Chroma db.

        :param schema: Схема, определяющая индекс и структуру данных для вставки.
        :param data: Список или представление значений, содержащих документы для вставки.
        """
        actions = (
            {
                "_index": schema._index,
                "_id": document["id"],
                "_source": schema(**document).dict(),
            }
            for document in data
        )
        actions_list = list(actions)
        films = []
        for action in actions_list:
            if action["_index"] == "movies":
                film = dict(action["_source"])
                logger.debug(f"{__name__}: movie: " f"\n{film}")
                films.append(film)

        logger.debug(f"movies data: \n{actions_list}")
        helpers.bulk(self.elastic, actions_list, chunk_size=BATCH_SIZE)
        self.vector_loader.load_vectors(films)
