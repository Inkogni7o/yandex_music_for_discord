from pydantic import BaseModel, ConfigDict, Field
from PySide6.QtCore import QSettings

from src.core.settings import RpcSettings


class AppSettings(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    discord_app_id: str = ""
    update_interval: int = Field(default=2, ge=1, le=30)
    start_rpc_on_launch: bool = False
    close_to_tray: bool = True

    def rpc_settings(self) -> RpcSettings:
        return RpcSettings(
            update_interval=self.update_interval,
        )


class SettingsStore:
    def __init__(self) -> None:
        self._settings = QSettings()

    def load(self) -> AppSettings:
        return AppSettings(
            discord_app_id=self._settings.value("discord/app_id", "", str),
            update_interval=self._settings.value("rpc/update_interval", 2, int),
            start_rpc_on_launch=self._settings.value(
                "app/start_rpc_on_launch", False, bool
            ),
            close_to_tray=self._settings.value("app/close_to_tray", True, bool),
        )

    def save(self, settings: AppSettings) -> None:
        self._settings.setValue("discord/app_id", settings.discord_app_id)
        self._settings.setValue("rpc/update_interval", settings.update_interval)
        self._settings.setValue(
            "app/start_rpc_on_launch", settings.start_rpc_on_launch
        )
        self._settings.setValue("app/close_to_tray", settings.close_to_tray)
        self._settings.sync()
