import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from src.app.main_window import MainWindow
from src.app.single_instance import SingleInstance
from src.app.theme import apply_theme


def run() -> int:
    QCoreApplication.setOrganizationName("YandexMusicForDiscord")
    QCoreApplication.setApplicationName("YandexMusicRichPresence")

    app = QApplication(sys.argv)
    apply_theme(app)

    single_instance = SingleInstance()
    is_primary_instance = single_instance.acquire()
    if not is_primary_instance:
        return 0

    app.setQuitOnLastWindowClosed(not QSystemTrayIcon.isSystemTrayAvailable())
    window = MainWindow()
    single_instance.activation_requested.connect(window.show_and_activate)
    window.show()
    return app.exec()
