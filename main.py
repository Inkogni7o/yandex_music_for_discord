import asyncio
import time

from pypresence import AioPresence
from pypresence.types import ActivityType
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)

from config import DISCORD_APP_ID
from src.core.covers import YandexTrackMatch, find_exact_track
from src.core.media import NowPlaying, get_now_playing

POLL_INTERVAL_SECONDS = 2
SEEK_TOLERANCE_SECONDS = 5


def calculate_position_shift(
    current_position: float,
    previous_position: float,
    elapsed_seconds: float,
) -> float:
    expected_position = previous_position + elapsed_seconds
    return current_position - expected_position


async def publish_presence(
    rpc: AioPresence,
    now_playing: NowPlaying,
    matched_track: YandexTrackMatch,
) -> None:
    started_at = int(time.time() - now_playing.position_seconds)
    await rpc.update(
        activity_type=ActivityType.LISTENING,
        details=now_playing.title,
        state=now_playing.artist or "Неизвестный исполнитель",
        start=started_at,
        large_image=matched_track.cover_url,
    )


async def run() -> None:
    try:
        media_manager = await MediaSessionManager.request_async()
    except OSError as error:
        raise RuntimeError(
            "Windows Media Session недоступен. Запустите программу из обычного "
            "пользовательского терминала, а не как службу или от имени SYSTEM."
        ) from error

    rpc = AioPresence(client_id=DISCORD_APP_ID)
    await rpc.connect()

    observed_track: tuple[str, str] | None = None
    matched_track: YandexTrackMatch | None = None
    presence_is_visible = False
    last_position_seconds: float | None = None
    last_position_sampled_at: float | None = None

    try:
        while True:
            sampled_at = time.monotonic()
            now_playing = await get_now_playing(media_manager)

            if now_playing is None:
                if presence_is_visible:
                    await rpc.clear()
                    presence_is_visible = False
                    print("Воспроизведение остановлено")
                observed_track = None
                matched_track = None
                last_position_seconds = None
                last_position_sampled_at = None
            elif now_playing.key != observed_track:
                observed_track = now_playing.key
                matched_track = await asyncio.to_thread(
                    find_exact_track,
                    now_playing.title,
                    now_playing.artist,
                )
                if matched_track is None:
                    if presence_is_visible:
                        await rpc.clear()
                        presence_is_visible = False
                    print(
                        "Медиа пропущено: нет совпадения в Яндекс Музыке — "
                        f"{now_playing.artist} — {now_playing.title}"
                    )
                else:
                    await publish_presence(rpc, now_playing, matched_track)
                    presence_is_visible = True
                    print(f"Сейчас играет: {now_playing.artist} — {now_playing.title}")
            elif (
                matched_track is not None
                and presence_is_visible
                and last_position_seconds is not None
                and last_position_sampled_at is not None
            ):
                position_shift = calculate_position_shift(
                    current_position=now_playing.position_seconds,
                    previous_position=last_position_seconds,
                    elapsed_seconds=sampled_at - last_position_sampled_at,
                )
                if abs(position_shift) >= SEEK_TOLERANCE_SECONDS:
                    await publish_presence(rpc, now_playing, matched_track)
                    print(f"Перемотка: {position_shift:+.1f} с")

            if now_playing is not None:
                last_position_seconds = now_playing.position_seconds
                last_position_sampled_at = sampled_at

            await asyncio.sleep(POLL_INTERVAL_SECONDS)
    finally:
        if rpc.sock_writer is not None:
            rpc.sock_writer.close()
            await rpc.sock_writer.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
