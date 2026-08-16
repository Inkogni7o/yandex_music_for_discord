import re
import unicodedata
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field
from yandex_music import Client, Track

_music_client = Client()


class YandexTrackMatch(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    title: str = Field(min_length=1)
    artists: tuple[str, ...] = Field(min_length=1)
    cover_url: str | None = None


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("\u0451", "\u0435")
    return " ".join(re.findall(r"\w+", value))


def _is_exact_match(track: Track, title: str, artist: str) -> bool:
    if not artist.strip():
        return False

    candidate_artists = ", ".join(track.artists_name())
    return _normalize(track.title) == _normalize(title) and _normalize(
        candidate_artists
    ) == _normalize(artist)


@lru_cache(maxsize=256)
def find_exact_track(title: str, artist: str) -> YandexTrackMatch | None:
    search = _music_client.search(
        f"{artist} {title}".strip(),
        type_="track",
    )
    if search is None or search.tracks is None:
        return None

    track = next(
        (
            track
            for track in search.tracks.results
            if _is_exact_match(track, title, artist)
        ),
        None,
    )
    if track is None:
        return None

    return YandexTrackMatch(
        title=track.title,
        artists=tuple(track.artists_name()),
        cover_url=(track.get_cover_url("1000x1000") if track.cover_uri else None),
    )
