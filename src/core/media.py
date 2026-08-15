from dataclasses import dataclass

from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
)


@dataclass(frozen=True, slots=True)
class NowPlaying:
    title: str
    artist: str
    album: str
    position_seconds: float
    source_app: str

    @property
    def key(self) -> tuple[str, str]:
        return self.title, self.artist


async def get_now_playing(
    manager: GlobalSystemMediaTransportControlsSessionManager,
) -> NowPlaying | None:
    session = manager.get_current_session()
    if session is None:
        return None

    playback = session.get_playback_info()
    if playback.playback_status != PlaybackStatus.PLAYING:
        return None

    properties = await session.try_get_media_properties_async()
    if properties is None or not properties.title.strip():
        return None

    timeline = session.get_timeline_properties()

    return NowPlaying(
        title=properties.title.strip(),
        artist=properties.artist.strip(),
        album=properties.album_title.strip(),
        position_seconds=max(0.0, timeline.position.total_seconds()),
        source_app=session.source_app_user_model_id,
    )
