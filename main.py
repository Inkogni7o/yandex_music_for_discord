import asyncio

from config import DISCORD_APP_ID
from src.core.run_presence import run_presence

if __name__ == "__main__":
    try:
        asyncio.run(run_presence(DISCORD_APP_ID))
    except KeyboardInterrupt:
        pass
