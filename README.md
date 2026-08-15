# Rich presence for Yandex Music

## Setup

1. Install the dependencies:

   ```powershell
   uv sync
   ```

2. Get a Yandex Music token through OAuth Device Flow:

   ```powershell
   uv run python -m src.core.get_yandex_token
   ```

   Open the displayed URL, enter the code, and confirm access.

3. Copy `config.example.py` to `config.py` and fill in `YANDEX_TOKEN` and
   `DISCORD_APP_ID`. The local `config.py` is excluded from Git.

4. Start Discord and run:

   ```powershell
   uv run python main.py
   ```
