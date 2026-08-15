import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache

from yandex_music import Client, Track
from yandex_music.exceptions import YandexMusicError

MINIMUM_MATCH_SCORE = 0.7
_music_client = Client()


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"\w+", value))


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()


def _match_score(track: Track, title: str, artist: str) -> float:
    title_score = _similarity(title, track.title)
    if not artist:
        return title_score

    candidate_artists = ", ".join(track.artists_name())
    artist_score = _similarity(artist, candidate_artists)
    return title_score * 0.7 + artist_score * 0.3


@lru_cache(maxsize=256)
def find_cover_url(title: str, artist: str) -> str | None:
    try:
        search = _music_client.search(
            f"{artist} {title}".strip(),
            type_="track",
        )
    except YandexMusicError as error:
        print(f"Не удалось найти обложку: {error}")
        return None

    if search is None or search.tracks is None:
        return None

    candidates = [
        (_match_score(track, title, artist), track)
        for track in search.tracks.results
        if track.cover_uri
    ]
    if not candidates:
        return None

    score, track = max(candidates, key=lambda candidate: candidate[0])
    if score < MINIMUM_MATCH_SCORE:
        return None

    return track.get_cover_url("1000x1000")
