from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Security

from api.utils import has_access_to_questionable_content, verify_jwt_scopes
from api.v1.api_models.film import FilmDetail, FilmShort

from core.caching import cache
from core.config import DEFAULT_PAGE, MAX_PER_PAGE, PER_PAGE, ELASTIC_MAX_RESULT_WINDOW, QUESTIONABLE_GENRE
from services.film import FilmService, get_film_service

film_router = APIRouter()


@film_router.get(
    '/',
    response_model=List[FilmShort],
    summary='All movies',
    description='All movies sorted by a parameter',
    response_description='Name and rating of a movie',
)
@cache(prefix='sorted_films')
async def film_sorted(
        sort: str = Query(..., regex=r'^(\w|-)\w+', min_length=1, max_length=20),
        page: int = Query(DEFAULT_PAGE, gt=0, le=ELASTIC_MAX_RESULT_WINDOW),
        page_size: int = Query(PER_PAGE, gt=0, le=MAX_PER_PAGE),
        genre: Optional[str] = Query(None, min_length=1, max_length=20),
        has_access: bool = Depends(has_access_to_questionable_content),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    """Films sorted by a parameter.
    """
    films = await film_service.get_sorted(sort, page, page_size, genre)

    if not has_access:
        films = [f for f in films if QUESTIONABLE_GENRE not in f.genres]

    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')

    return [FilmShort(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@film_router.get(
    '/premium',
    dependencies=[Security(verify_jwt_scopes, scopes=['premium'])],    # strict authorized access
    response_model=List[FilmShort],
    summary='All premium movies',
    description='All premium movies sorted by a parameter',
    response_description='Name and rating of a premium movies',
)
@cache(prefix='sorted_premium_films')
async def film_sorted(
        sort: str = Query(..., regex=r'^(\w|-)\w+', min_length=1, max_length=20),
        page: int = Query(DEFAULT_PAGE, gt=0, le=ELASTIC_MAX_RESULT_WINDOW),
        page_size: int = Query(PER_PAGE, gt=0, le=MAX_PER_PAGE),
        genre: Optional[str] = Query(None, min_length=1, max_length=20),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    """Premium films sorted by a parameter.
    """
    films = await film_service.get_sorted(sort, page, page_size, genre)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')

    return [FilmShort(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@film_router.get(
    '/search',
    response_model=List[FilmShort],
    summary='Movie search',
    description='Text search for movies',
    response_description='Name and rating of a movie',
)
@cache(prefix='film_search')
async def film_search(
        query: str = Query(..., min_length=1, max_length=255),
        page: int = Query(DEFAULT_PAGE, gt=0, le=ELASTIC_MAX_RESULT_WINDOW),
        page_size: int = Query(PER_PAGE, gt=0, le=MAX_PER_PAGE),
        has_access: bool = Depends(has_access_to_questionable_content),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    """Films sorted by a parameter.
    """
    films = await film_service.get_search(query, page, page_size)

    if not has_access:
        films = [f for f in films if QUESTIONABLE_GENRE not in f.genres]

    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='films not found')

    return [FilmShort(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@film_router.get(
    '/{film_id}',
    response_model=FilmDetail,
    summary='Information about a movie',
    description='Full information about a movie',
    response_description=(
        'Title, description, rating, genre and people that participated in a movie'
    ),
)
@cache(prefix='film_details')
async def film_details(
        film_id: str = Path(..., title='The id of the film to get.', min_length=1, max_length=255),
        has_access: bool = Depends(has_access_to_questionable_content),
        film_service: FilmService = Depends(get_film_service)
) -> FilmDetail:
    """Detailed information about a film.
    """
    film = await film_service.get_by_id(film_id)

    if not has_access and QUESTIONABLE_GENRE in film.genres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='film not found')

    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='film not found')

    return FilmDetail(
        uuid=film.uuid,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )
