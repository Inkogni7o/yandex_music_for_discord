import time
from datetime import datetime

from pypresence import Presence
from yandex_music import Client

from config import YANDEX_TOKEN, DISCORD_APP_ID

UPDATE_INTERVAL_SECONDS = 15

# Yandex token. You can get it from "get_yandex_token.py"
TOKEN = YANDEX_TOKEN

# This is Aplications ID
client_id = DISCORD_APP_ID

# Inicalize the RPC
RPC = Presence(client_id=client_id)
RPC.connect()

# Inicalize Yandex Music API
client = Client(TOKEN).init()
start_time = datetime.now()

# subprocess.Popen(way_to_Yandex_music)

# Work until the program doesnt stopped
while True:
    try:
        queues = client.queues_list()
        last_queue = client.queue(queues[0].id)
        last_track_id = last_queue.get_current_track()
        last_track = last_track_id.fetch_track()
        artists = ", ".join(last_track.artists_name())
        title = last_track.title
        track_link = f"https://music.yandex.ru/album/{last_track['albums'][0]['id']}/track/{last_track['id']}/"
        image_link = "https://" + last_track.cover_uri.replace("%%", "1000x1000")

        timedelta = datetime.now() - start_time

        RPC.update(
            details="Слушает: " + title,
            state="Прошло: " + ":".join(str(timedelta).split(".")[:-1]),
            large_image=image_link,
            large_text="Исполнитель: " + artists,
            small_image="https://sun2.beeline-yaroslavl.userapi.com/s/v1/ig2/ayvI4btzEaAgH5885Sg0"
            "OwZud3jH3daU2LzP8KfTFvv0yLNzd2RBPc1PBxPrQfrfdC_vreCXfBcYhO8TzFgwJdpK.jpg?"
            "size=2560x2560&quality=95&type=album",
        )

    except:
        RPC.update(
            details="Поддерживаются только треки из плейлистов 😥",
            state="Попробуй включить трек из плейлистов 🙃",
            large_image="https://c.tenor.com/ZuIbNWpIN5MAAAAC/rias-gremory-high-school-dxd.gif",
        )

    time.sleep(UPDATE_INTERVAL_SECONDS)
