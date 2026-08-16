from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QFrame,
    QSpinBox,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.rpc_controller import RpcController
from src.app.settings import AppSettings, SettingsStore


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._store = SettingsStore()
        self._settings = self._store.load()
        self._controller = RpcController()
        self._quit_requested = False
        self._tray_hint_was_shown = False

        self.setWindowTitle("Yandex Music Rich Presence")
        self.setMinimumSize(580, 420)
        self.resize(640, 460)
        self._set_icon()
        self._build_ui()
        self._build_tray()
        self._apply_settings(self._settings)
        self._connect_signals()

        if self._settings.start_rpc_on_launch and self._valid_app_id(
            self._settings.discord_app_id
        ):
            self._start_rpc()

    def _set_icon(self) -> None:
        icon_path = Path(__file__).parent / "static" / "label.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setDocumentMode(False)
        tabs.addTab(self._build_general_tab(), "Главная")
        tabs.addTab(self._build_rpc_settings_tab(), "Настройки RPC")
        root_layout.addWidget(tabs)
        self.setCentralWidget(root)

    def _build_general_tab(self) -> QWidget:
        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("Yandex Music  ×  Discord")
        title.setObjectName("title")
        description = QLabel(
            "Укажите Application ID из Discord Developer Portal, затем включите RPC."
        )
        description.setWordWrap(True)
        description.setObjectName("muted")

        app_id_group = QGroupBox("Подключение")
        form = QFormLayout(app_id_group)
        self.app_id_edit = QLineEdit()
        self.app_id_edit.setPlaceholderText("Например, 123456789012345678")
        self.app_id_edit.setMaxLength(25)
        self.app_id_edit.setClearButtonEnabled(True)
        form.addRow("Discord App ID", self.app_id_edit)

        controls = QHBoxLayout()
        self.toggle_button = QPushButton("Включить RPC")
        self.toggle_button.setObjectName("primary")
        self.toggle_button.setProperty("running", False)
        self.toggle_button.setMinimumHeight(38)
        self.toggle_button.setFixedWidth(190)
        controls.addWidget(self.toggle_button)
        controls.addStretch()

        status_panel = QFrame()
        status_panel.setObjectName("statusPanel")
        status_row = QHBoxLayout(status_panel)
        status_row.setContentsMargins(14, 10, 14, 10)
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setProperty("state", "off")
        status_caption = QLabel("Статус:")
        self.status_label = QLabel("RPC выключен")
        self.status_label.setObjectName("status")
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        status_row.addWidget(self.status_indicator)
        status_row.addWidget(status_caption)
        status_row.addWidget(self.status_label, 1)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(app_id_group)
        layout.addLayout(controls)
        layout.addStretch()
        layout.addWidget(status_panel)
        return page

    def _build_rpc_settings_tab(self) -> QWidget:
        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        behavior_group = QGroupBox("Поведение")
        behavior_layout = QFormLayout(behavior_group)
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(1, 30)
        self.update_interval_spin.setSuffix(" сек.")
        behavior_layout.addRow("Интервал обновления", self.update_interval_spin)
        self.start_on_launch_check = QCheckBox("Включать RPC при запуске приложения")
        self.close_to_tray_check = QCheckBox("Сворачивать в трей при закрытии окна")
        behavior_layout.addRow(self.start_on_launch_check)
        behavior_layout.addRow(self.close_to_tray_check)

        note = QLabel(
            "Изменения параметров RPC применятся при следующем включении."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")

        layout.addWidget(behavior_group)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        menu = QMenu()
        show_action = QAction("Открыть", self)
        show_action.triggered.connect(self.show_and_activate)
        self.tray_rpc_action = QAction("Включить RPC", self)
        self.tray_rpc_action.triggered.connect(self._toggle_rpc)
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self._quit)
        menu.addAction(show_action)
        menu.addAction(self.tray_rpc_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def _connect_signals(self) -> None:
        self.toggle_button.clicked.connect(self._toggle_rpc)
        self.app_id_edit.editingFinished.connect(self._save_settings)
        self.update_interval_spin.valueChanged.connect(self._save_settings)
        self.start_on_launch_check.toggled.connect(self._save_settings)
        self.close_to_tray_check.toggled.connect(self._save_settings)
        self._controller.status_changed.connect(self._on_status_changed)
        self._controller.running_changed.connect(self._on_running_changed)
        self._controller.failed.connect(self._show_rpc_error)

    def _apply_settings(self, settings: AppSettings) -> None:
        self.app_id_edit.setText(settings.discord_app_id)
        self.update_interval_spin.setValue(settings.update_interval)
        self.start_on_launch_check.setChecked(settings.start_rpc_on_launch)
        self.close_to_tray_check.setChecked(settings.close_to_tray)

    def _current_settings(self) -> AppSettings:
        return AppSettings(
            discord_app_id=self.app_id_edit.text(),
            update_interval=self.update_interval_spin.value(),
            start_rpc_on_launch=self.start_on_launch_check.isChecked(),
            close_to_tray=self.close_to_tray_check.isChecked(),
        )

    def _save_settings(self, *_args: object) -> None:
        self._settings = self._current_settings()
        self._store.save(self._settings)

    @staticmethod
    def _valid_app_id(app_id: str) -> bool:
        return app_id.isdigit() and 15 <= len(app_id) <= 25

    def _toggle_rpc(self) -> None:
        if self._controller.is_running:
            self._controller.stop()
        else:
            self._start_rpc()

    def _start_rpc(self) -> None:
        self._save_settings()
        if not self._valid_app_id(self._settings.discord_app_id):
            QMessageBox.warning(
                self,
                "Некорректный App ID",
                "Discord App ID должен состоять из 15–25 цифр.",
            )
            self.app_id_edit.setFocus()
            return
        self._controller.start(
            self._settings.discord_app_id,
            self._settings.rpc_settings(),
        )

    def _on_running_changed(self, running: bool) -> None:
        self.toggle_button.setText("Выключить RPC" if running else "Включить RPC")
        self.tray_rpc_action.setText(
            "Выключить RPC" if running else "Включить RPC"
        )
        self.app_id_edit.setEnabled(not running)
        self.toggle_button.setProperty("running", running)
        self.toggle_button.style().unpolish(self.toggle_button)
        self.toggle_button.style().polish(self.toggle_button)

    def _on_status_changed(self, status: str) -> None:
        self.status_label.setText(status)
        if status.startswith("Ошибка"):
            state = "error"
        elif status == "RPC включён":
            state = "active"
        elif status.endswith("…"):
            state = "pending"
        else:
            state = "off"
        self.status_indicator.setProperty("state", state)
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)

    def _show_rpc_error(self, message: str) -> None:
        QMessageBox.critical(
            self,
            "Не удалось включить RPC",
            f"Проверьте, что Discord запущен и App ID указан верно.\n\n{message}",
        )

    def show_and_activate(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_and_activate()

    def _quit(self) -> None:
        self._quit_requested = True
        self._controller.stop()
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if (
            not self._quit_requested
            and self.close_to_tray_check.isChecked()
            and QSystemTrayIcon.isSystemTrayAvailable()
        ):
            event.ignore()
            self.hide()
            if not self._tray_hint_was_shown:
                self.tray.showMessage(
                    "Yandex Music Rich Presence",
                    "Приложение продолжает работать в трее.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2500,
                )
                self._tray_hint_was_shown = True
            return

        self._controller.stop()
        self._quit_requested = True
        self.tray.hide()
        event.accept()
        QApplication.quit()
