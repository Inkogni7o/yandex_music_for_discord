# Yandex Music Rich Presence

Десктопное Windows-приложение, которое показывает текущий трек из системной
медиасессии в Discord Rich Presence. Обложка находится через публичный поиск
Яндекс Музыки.

## Возможности

- ввод и сохранение Discord Application ID;
- включение и выключение RPC без перезапуска приложения;
- постоянное отображение обложки и таймера;
- настройка интервала обновления;
- автоматическое включение RPC при запуске;
- работа из системного трея.
- защита от повторного запуска с активацией уже открытого окна.

## Запуск для разработки

1. Установите зависимости:

   ```powershell
   uv sync --locked
   ```

2. Запустите приложение:

   ```powershell
   uv run python main.py
   ```

Application ID создаётся в
[Discord Developer Portal](https://discord.com/developers/applications/). Для
работы RPC должен быть запущен десктопный клиент Discord.

## Сборка EXE

Сборка выполняется на Windows через PyInstaller:

```powershell
uv run pyinstaller --noconfirm --clean yandex_music_rpc.spec
```

Готовый файл появится в `dist/YandexMusicRPC.exe`.
