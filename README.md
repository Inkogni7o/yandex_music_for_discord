# Rich presence for Yandex Music

Shows the track playing in the active Windows media session as Discord Rich
Presence. Track metadata comes from Windows; Yandex Music is queried
anonymously only when a new track needs a public cover URL.

## Setup

1. Install the dependencies:

   ```powershell
   uv sync --locked
   ```

2. Copy `config.example.py` to `config.py` and set `DISCORD_APP_ID`. Create the
   application ID at <https://discord.com/developers/applications/>.

3. Start Discord and play music in a Windows media-enabled application such as
   Firefox or Edge.

4. Run the integration from your normal user terminal:

   ```powershell
   uv run python main.py
   ```
