import asyncio
import time

from pypresence import AioPresence
from pypresence.types import ActivityType
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)

from config import DISCORD_APP_ID
from src.core.covers import find_cover_url
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

    published_track: tuple[str, str] | None = None
    presence_is_visible = False

    try:
        while True:
            now_playing = await get_now_playing(media_manager)

            if now_playing is None:
                if presence_is_visible:
                    await rpc.clear()
                    published_track = None
                    presence_is_visible = False
                    print("Воспроизведение остановлено")
            elif now_playing.key != published_track:
                cover_url = await asyncio.to_thread(
                    find_cover_url,
                    now_playing.title,
                    now_playing.artist,
                )
                started_at = int(time.time() - now_playing.position_seconds)

                await rpc.update(
                    activity_type=ActivityType.LISTENING,
                    details=now_playing.title,
                    state=now_playing.artist or "Неизвестный исполнитель",
                    start=started_at,
                    large_image=cover_url,
                    large_text=now_playing.album or "Яндекс Музыка",
                )

                published_track = now_playing.key
                presence_is_visible = True
                print(
                    f"Сейчас играет: {now_playing.artist} — {now_playing.title} "
                    f"[{now_playing.source_app}]"
                )

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
