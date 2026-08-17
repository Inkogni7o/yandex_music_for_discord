# Yandex Music Rich Presence

Небольшое приложение для Windows, которое показывает текущий трек из Яндекс Музыки в профиле Discord. В статусе отображаются название, исполнитель, обложка и время воспроизведения.

Работает как с десктоп, так и с веб версией Я.Музыки. Может работать во всех режимах, включая "Моя волна"

## Скачать приложение

1. Откройте страницу [последнего релиза](https://github.com/Inkogni7o/yandex_music_for_discord/releases/latest).
2. Скачайте файл `YandexMusicRPC.exe`.
3. Запустите его. Установка и отдельно установленный Python не требуются.

Приложение предназначено для Windows 10 и Windows 11. Для его работы нужны запущенный десктопный клиент Discord.

## Первая настройка

Приложению нужен Application ID из Discord Developer Portal. Это публичный
идентификатор приложения.

1. Откройте [Discord Developer Portal](https://discord.com/developers/applications/).
2. Нажмите `New Application` и создайте приложение с любым названием.
3. На странице `General Information` скопируйте значение `Application ID`.
4. Вставьте его в поле `Discord App ID` в Yandex Music Rich Presence.
5. Нажмите `Включить RPC` и запустите трек в Яндекс Музыке.

После подключения приложение можно свернуть или закрыть в системный трей. Убедитесь, что в Discord включено отображение текущей активности.

## Запуск из исходников

Установите зависимости:

```powershell
uv sync --locked
```

Запустите приложение:

```powershell
uv run python main.py
```

## Сборка EXE

Сборка выполняется на Windows через PyInstaller:

```powershell
uv run pyinstaller --noconfirm --clean yandex_music_rpc.spec
```

Готовый файл появится в `dist/YandexMusicRPC.exe`.
