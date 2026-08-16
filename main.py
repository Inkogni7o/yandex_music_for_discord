import asyncio
import time

from pypresence import AioPresence
from pypresence.types import ActivityType
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)

from config import DISCORD_APP_ID
from src.core.covers import find_exact_track
from src.core.media import get_now_playing

POLL_INTERVAL_SECONDS = 2


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
    presence_is_visible = False

    try:
        while True:
            now_playing = await get_now_playing(media_manager)

            if now_playing is None:
                if presence_is_visible:
                    await rpc.clear()
                    presence_is_visible = False
                    print("Воспроизведение остановлено")
                observed_track = None
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
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue

                started_at = int(time.time() - now_playing.position_seconds)

                await rpc.update(
                    activity_type=ActivityType.LISTENING,
                    details=now_playing.title,
                    state=now_playing.artist or "Неизвестный исполнитель",
                    start=started_at,
                    large_image=matched_track.cover_url,
                )

                presence_is_visible = True
                print(f"Сейчас играет: {now_playing.artist} — {now_playing.title}")

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
