from typing import TypedDict

from module.conf import TMDB_API
from module.network import RequestContent

from .baseapi import BaseAPI

TMDB_URL = "https://api.themoviedb.org"
TMDB_IMG_URL = "https://image.tmdb.org/t/p/w780"


class ShowInfo(TypedDict):
    adult: bool
    backdrop_path: str
    genre_ids: list[int]
    id: int
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str
    first_air_date: str
    name: str
    vote_average: float
    vote_count: int


class Genre(TypedDict):
    id: int
    name: str


class Network(TypedDict):
    id: int
    logo_path: str | None
    name: str
    origin_country: str


class LastEpisodeToAir(TypedDict):
    id: int
    name: str
    overview: str
    vote_average: float
    vote_count: int
    air_date: str
    episode_number: int
    episode_type: str
    production_code: str
    runtime: int
    season_number: int
    show_id: int
    still_path: str


class ProductionCompany(TypedDict):
    id: int
    name: str
    origin_country: str
    logo_path: str


class Season(TypedDict):
    air_date: str | None
    episode_count: int
    id: int
    name: str
    overview: str
    season_number: int
    vote_average: float
    poster_path: str


class TVShow(TypedDict):
    adult: bool
    backdrop_path: str
    # 不知道是什么类型, 都是[]
    created_by: list[str]
    episode_run_time: list[int]
    # 就像是"2024-04-12"
    first_air_date: str
    genres: list[Genre]
    homepage: str
    id: int
    in_production: bool
    languages: list[str]
    last_air_date: str
    last_episode_to_air: str
    name: str
    networks: list[Network]
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str
    production_companies: list[ProductionCompany]
    production_countries: list[dict[str, str]]
    seasons: list[Season]
    next_episode_to_air: str


LANGUAGE = {"zh": "zh-CN", "jp": "ja-JP", "en": "en-US"}


def search_url(e: str) -> str:
    return f"{TMDB_URL}/3/search/tv?api_key={TMDB_API}&page=1&query={e}&include_adult=false"


def info_url(id: str, language: str) -> str:
    return f"{TMDB_URL}/3/tv/{id}?api_key={TMDB_API}&language={LANGUAGE[language]}"


class TMDBSearchAPI:
    async def get_content(self, key_word: str) -> list[ShowInfo]:
        async with RequestContent() as req:
            url = search_url(key_word)
            json_contents = await req.get_json(url)
            contents: list[ShowInfo] = json_contents.get("results", [])
            return contents if contents else []


class TMDBInfoAPI:
    async def get_content(self, id: str, language: str) -> TVShow:
        async with RequestContent() as req:
            url = info_url(id, language)
            json_contents = await req.get_json(url)
            return json_contents
