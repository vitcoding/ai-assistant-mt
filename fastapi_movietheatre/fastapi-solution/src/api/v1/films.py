from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

# from core.jaeger import tracer
from opentelemetry import trace
from pydantic import BaseModel

from services.film import FilmService, get_film_service
from services.films import FilmListService, get_film_list_service
from services.films_search import (
    FilmListSearchService,
    get_film_list_search_service,
)
from services.security.access import JWTBearer, security_jwt

router = APIRouter()

tracer = trace.get_tracer(__name__)


# Модель ответа API (список кинопроизведений)
class FilmList(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None


# Модель ответа API (кинопроизведение)
class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list
    actors: list
    writers: list
    directors: list


@router.get(
    "/",
    response_model=list[FilmList],
    summary="Список кинопроизведений",
    description="Постраничный список кинопроизведений",
    response_description="Название и рейтинг кинопроизведения",
)
async def film_list(
    sort: str | None = Query("-imdb_rating"),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    genre: str = Query(None),
    film_service: FilmListService = Depends(get_film_list_service),
) -> list[FilmList]:
    with tracer.start_as_current_span("film_list") as span:
        span.set_attribute("sort", sort)
        span.set_attribute("page_size", page_size)
        span.set_attribute("page_number", page_number)
        span.set_attribute("genre", genre)
        films = await film_service.get_list(
            sort, page_size, page_number, genre
        )
        if not films:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="films not found"
            )
        return [FilmList(**dict(film)) for film in films]


@router.get(
    "/search",
    response_model=list[FilmList],
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг кинопроизведения",
)
async def search_film_list(
    query: str | None = Query(None),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    film_service: FilmListSearchService = Depends(
        get_film_list_search_service
    ),
    access_data: JWTBearer = Depends(security_jwt),
) -> list[FilmList]:
    films = await film_service.get_list(query, page_size, page_number)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="films not found"
        )
    return [FilmList(**dict(film)) for film in films]


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Кинопроизведение",
    description="Данные по кинопроизведению",
    response_description="Название, рейтинг, оисание, жанры "
    + "и роли кинопроизведения",
)
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service),
    access_data: JWTBearer = Depends(security_jwt),
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="film not found"
        )
    return Film(**dict(film))
