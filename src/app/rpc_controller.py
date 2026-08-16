"""Background lifecycle controller for Discord RPC."""

import asyncio
import threading

from PySide6.QtCore import QObject, Signal

from src.core.run_presence import run_presence
from src.core.settings import RpcSettings


class RpcController(QObject):
    status_changed = Signal(str)
    running_changed = Signal(bool)
    failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self._stop_event: threading.Event | None = None
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self, app_id: str, settings: RpcSettings) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event = threading.Event()
            self._thread = threading.Thread(
                target=self._run,
                args=(app_id, settings, self._stop_event),
                name="discord-rpc",
                daemon=True,
            )
            thread = self._thread

        self.status_changed.emit("Подключение к Discord…")
        self.running_changed.emit(True)
        thread.start()

    def stop(self) -> None:
        with self._lock:
            stop_event = self._stop_event
        if stop_event is not None:
            self.status_changed.emit("Отключение RPC…")
            stop_event.set()

    def _run(
        self,
        app_id: str,
        settings: RpcSettings,
        stop_event: threading.Event,
    ) -> None:
        error_message: str | None = None
        try:
            asyncio.run(
                run_presence(
                    app_id,
                    settings=settings,
                    stop_event=stop_event,
                    on_connected=lambda: self.status_changed.emit("RPC включён"),
                )
            )
        except Exception as error:
            if not stop_event.is_set():
                error_message = str(error) or type(error).__name__
        finally:
            with self._lock:
                if self._stop_event is stop_event:
                    self._thread = None
                    self._stop_event = None

            self.running_changed.emit(False)
            if error_message is None:
                self.status_changed.emit("RPC выключен")
            else:
                self.status_changed.emit(f"Ошибка: {error_message}")
                self.failed.emit(error_message)
