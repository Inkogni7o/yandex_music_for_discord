from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSession,
    GlobalSystemMediaTransportControlsSessionManager,
)
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
)


class NowPlaying(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    title: str = Field(min_length=1)
    artist: str
    album: str
    position_seconds: float = Field(ge=0)
    source_app: str = Field(min_length=1)

    @property
    def key(self) -> tuple[str, str]:
        return self.title, self.artist


async def get_now_playing(
    manager: GlobalSystemMediaTransportControlsSessionManager,
) -> NowPlaying | None:
    sessions = await get_playing_media(manager)
    return sessions[0] if sessions else None


async def get_playing_media(
    manager: GlobalSystemMediaTransportControlsSessionManager,
) -> tuple[NowPlaying, ...]:
    current_session = manager.get_current_session()
    current_source = (
        current_session.source_app_user_model_id if current_session else None
    )
    sessions = sorted(
        manager.get_sessions(),
        key=lambda session: session.source_app_user_model_id != current_source,
    )

    playing_media: list[NowPlaying] = []
    for session in sessions:
        try:
            media = await _get_session_media(session)
        except OSError:
            continue
        if media is not None:
            playing_media.append(media)
    return tuple(playing_media)


async def _get_session_media(
    session: GlobalSystemMediaTransportControlsSession,
) -> NowPlaying | None:
    playback = session.get_playback_info()
    if playback.playback_status != PlaybackStatus.PLAYING:
        return None

    properties = await session.try_get_media_properties_async()
    if properties is None or not properties.title.strip():
        return None

    timeline = session.get_timeline_properties()
    updated_at = timeline.last_updated_time
    elapsed_since_update = max(
        0.0,
        (datetime.now(updated_at.tzinfo) - updated_at).total_seconds(),
    )
    position_seconds = timeline.position.total_seconds() + elapsed_since_update

    return NowPlaying(
        title=properties.title.strip(),
        artist=properties.artist.strip(),
        album=properties.album_title.strip(),
        position_seconds=max(0.0, position_seconds),
        source_app=session.source_app_user_model_id,
    )
