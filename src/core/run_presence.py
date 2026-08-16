from pypresence import AioPresence
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)

from src.core.presence_updater import PresenceUpdater


async def run_presence(discord_app_id: str) -> None:
    try:
        media_manager = await MediaSessionManager.request_async()
    except OSError as error:
        raise RuntimeError(
            "Windows Media Session недоступен. Запустите программу из обычного "
            "пользовательского терминала, а не как службу или от имени SYSTEM."
        ) from error

    rpc = AioPresence(client_id=discord_app_id)
    await rpc.connect()

    try:
        await PresenceUpdater(rpc, media_manager).run()
    finally:
        if rpc.sock_writer is not None:
            rpc.sock_writer.close()
            await rpc.sock_writer.wait_closed()
