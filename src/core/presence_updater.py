import asyncio
import time
from threading import Event
from typing import Any

from pypresence import AioPresence
from pypresence.types import ActivityType
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)

from src.core.covers import YandexTrackMatch, find_exact_track
from src.core.media import NowPlaying, get_playing_media
from src.core.settings import RpcSettings


def calculate_position_shift(
    current_position: float,
    previous_position: float,
    elapsed_seconds: float,
) -> float:
    expected_position = previous_position + elapsed_seconds
    return current_position - expected_position


class PresenceUpdater:
    def __init__(
        self,
        rpc: AioPresence,
        media_manager: MediaSessionManager,
        settings: RpcSettings,
        stop_event: Event,
    ) -> None:
        self._rpc = rpc
        self._media_manager = media_manager
        self._settings = settings
        self._stop_event = stop_event
        self._observed_track: tuple[str, str] | None = None
        self._matched_track: YandexTrackMatch | None = None
        self._presence_is_visible = False
        self._started_at: int | None = None
        self._last_position_seconds: float | None = None
        self._last_position_sampled_at: float | None = None

    async def run(self) -> None:
        while not self._stop_event.is_set():
            sampled_at = time.monotonic()
            playing_media = await get_playing_media(self._media_manager)
            if self._observed_track is not None and not any(
                media.key == self._observed_track for media in playing_media
            ):
                await self._handle_stopped()

            selection = await self._select_yandex_media(playing_media)
            now_playing = selection[0] if selection is not None else None

            if now_playing is None:
                await self._handle_stopped()
            elif now_playing.key != self._observed_track:
                await self._handle_new_media(now_playing, selection[1])
            else:
                await self._handle_possible_seek(now_playing, sampled_at)

            if now_playing is not None:
                self._last_position_seconds = now_playing.position_seconds
                self._last_position_sampled_at = sampled_at

            await asyncio.sleep(self._settings.update_interval)

    async def _select_yandex_media(
        self,
        playing_media: tuple[NowPlaying, ...],
    ) -> tuple[NowPlaying, YandexTrackMatch] | None:
        if self._observed_track is not None and self._matched_track is not None:
            current_media = next(
                (
                    media
                    for media in playing_media
                    if media.key == self._observed_track
                ),
                None,
            )
            if current_media is not None:
                return current_media, self._matched_track

        for media in playing_media:
            if not media.artist:
                continue
            try:
                matched_track = await asyncio.to_thread(
                    find_exact_track,
                    media.title,
                    media.artist,
                )
            except Exception as error:
                print(f"Не удалось проверить трек через Яндекс Музыку: {error}")
                continue
            if matched_track is not None:
                return media, matched_track

        return None

    async def _handle_stopped(self) -> None:
        if self._presence_is_visible:
            await self._hide_presence()
            print("Воспроизведение остановлено")

        self._observed_track = None
        self._matched_track = None
        self._started_at = None
        self._last_position_seconds = None
        self._last_position_sampled_at = None

    async def _handle_new_media(
        self,
        now_playing: NowPlaying,
        matched_track: YandexTrackMatch,
    ) -> None:
        self._observed_track = now_playing.key
        self._matched_track = matched_track
        self._started_at = int(time.time() - now_playing.position_seconds)
        await self._publish(now_playing)
        print(f"Сейчас играет: {now_playing.artist} — {now_playing.title}")

    async def _handle_possible_seek(
        self,
        now_playing: NowPlaying,
        sampled_at: float,
    ) -> None:
        if (
            not self._presence_is_visible
            or self._last_position_seconds is None
            or self._last_position_sampled_at is None
        ):
            return

        position_shift = calculate_position_shift(
            current_position=now_playing.position_seconds,
            previous_position=self._last_position_seconds,
            elapsed_seconds=sampled_at - self._last_position_sampled_at,
        )
        if abs(position_shift) >= self._settings.seek_tolerance_seconds:
            self._started_at = int(time.time() - now_playing.position_seconds)
            await self._publish(now_playing)
            print(f"Перемотка: {position_shift:+.1f} с")

    async def _publish(self, now_playing: NowPlaying) -> None:
        presence: dict[str, Any] = {
            "activity_type": ActivityType.LISTENING,
            "details": now_playing.title,
            "state": now_playing.artist or "Неизвестный исполнитель",
            "start": self._started_at
            or int(time.time() - now_playing.position_seconds),
        }
        if self._matched_track is not None and self._matched_track.cover_url:
            presence["large_image"] = self._matched_track.cover_url

        await self._rpc.update(**presence)
        self._presence_is_visible = True

    async def _hide_presence(self) -> None:
        if self._presence_is_visible:
            await self._rpc.clear()
            self._presence_is_visible = False
