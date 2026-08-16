from collections.abc import Callable
from threading import Event

from pypresence import AioPresence
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaSessionManager,
)

from src.core.presence_updater import PresenceUpdater
from src.core.settings import RpcSettings


async def run_presence(
    discord_app_id: str,
    settings: RpcSettings | None = None,
    stop_event: Event | None = None,
    on_connected: Callable[[], None] | None = None,
) -> None:
    settings = settings or RpcSettings()
    stop_event = stop_event or Event()

    try:
        media_manager = await MediaSessionManager.request_async()
    except OSError as error:
        raise RuntimeError(
            "Windows Media Session недоступен. Запустите программу из обычной "
            "пользовательской сессии, а не как службу или от имени SYSTEM."
        ) from error

    rpc = AioPresence(client_id=discord_app_id)
    await rpc.connect()
    if on_connected is not None:
        on_connected()

    try:
        await PresenceUpdater(rpc, media_manager, settings, stop_event).run()
    finally:
        try:
            await rpc.clear()
        except (OSError, ConnectionError):
            pass
        if rpc.sock_writer is not None:
            rpc.sock_writer.close()
