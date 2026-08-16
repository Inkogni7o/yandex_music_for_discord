"""Single-instance coordination for the desktop application."""

import hashlib

from PySide6.QtCore import QIODevice, QObject, QStandardPaths, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket


class SingleInstance(QObject):
    activation_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        app_data_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        user_suffix = hashlib.sha256(app_data_path.encode()).hexdigest()[:12]
        self._server_name = f"YandexMusicRPC-{user_suffix}"
        self._server = QLocalServer(self)
        self._server.setSocketOptions(
            QLocalServer.SocketOption.UserAccessOption
        )
        self._server.newConnection.connect(self._handle_connection)

    def acquire(self) -> bool:
        if self._notify_existing_instance():
            return False

        QLocalServer.removeServer(self._server_name)
        if self._server.listen(self._server_name):
            return True

        if self._notify_existing_instance():
            return False

        raise RuntimeError(
            f"Не удалось создать локальный канал {self._server_name}: "
            f"{self._server.errorString()}"
        )

    def _notify_existing_instance(self) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(
            self._server_name,
            QIODevice.OpenModeFlag.WriteOnly,
        )
        if not socket.waitForConnected(250):
            return False

        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(250)
        socket.disconnectFromServer()
        return True

    def _handle_connection(self) -> None:
        while self._server.hasPendingConnections():
            socket = self._server.nextPendingConnection()
            socket.disconnected.connect(socket.deleteLater)
            self.activation_requested.emit()
            socket.disconnectFromServer()
