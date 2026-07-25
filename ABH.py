from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio, os, json, redis
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
ABH = TelegramClient('didi_user_ultra.session', api_id, api_hash)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
@ABH.on(events.NewMessage(pattern=r"^(كود الجلسة|/session)$", outgoing=True))
async def send_session(event):
    session_string = ABH.session.save()
    with open(SESSION_FILE, "w") as f:
        f.write(session_string)
    await ABH.send_message("me", f" Session String:\n`{session_string}`")
    await event.edit(" تم إرسال الجلسة إلى الرسائل المحفوظة")
def LOADVARS():
    config_file = "var.json"
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            gidvar = data.get("gidvar")
            hidvar = data.get("hidvar")
            return gidvar, hidvar
    return None, None
gidvar, hidvar = LOADVARS()
