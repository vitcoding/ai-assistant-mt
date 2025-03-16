from fastapi import APIRouter

from api.v1 import auth, films, genres, persons

router = APIRouter()

router.include_router(
    films.router, prefix="/v1/films", tags=["Кинопроизведения"]
)
router.include_router(genres.router, prefix="/v1/genres", tags=["Жанры"])
router.include_router(persons.router, prefix="/v1/persons", tags=["Персоны"])
router.include_router(auth.router, prefix="/v1", tags=["Токен"])
