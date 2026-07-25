from telethon.tl.types import DocumentAttributeAudio
from telethon.tl.types import Message
from shortcuts import try_forward
from telethon import events
from ABH import *
import os, re
ABH_Asbo3={'Monday':'الاثنين','Tuesday':'الثلاثاء','Wednesday':'الأربعاء','Thursday':'الخميس','Friday':'الجمعة','Saturday':'السبت','Sunday':'الأحد'}
@ABH.on(events.NewMessage(pattern=r"^جلب(?: (.+))?$", outgoing=True))
async def get(event):
    input_link = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if reply and reply.media:
        await event.delete()
        await getfromevent(reply, "- تـم حفظ الوسائط من الرد ✓")
        return
    elif input_link:
        match = re.match(r"https://t\.me/c/(\d+)/(\d+)", input_link)
        if match:
            chat_id = int("-100" + match.group(1))
            msg_id = int(match.group(2))
            msg = await ABH.get_messages(chat_id, ids=msg_id)
            caption = "- تـم حفظ الوسائط من الرسالة ✓"
            if isinstance(msg, Message) and msg.media:
                await event.delete()
                await getfromevent(msg, caption)
                return
async def getfromevent(message, caption):
    x = await ABH.get_me()
    my_id = x.id
    uid = message.sender_id
    if uid == my_id:
        return
    media = await message.download_media()
    if not media:
        await ABH.send_message(my_id, "❌ لم يتم تحميل الوسائط من الرسالة.")
        return
    await ABH.send_file(my_id, media, caption=caption, parse_mode="markdown")
    if os.path.exists(media):
        os.remove(media)
def is_voice_note(message):
    if message.voice:
        return True
    if message.document:
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeAudio) and getattr(attr, 'voice', False):
                return True
    return False
def joker_unread_media(message):
    return (
        message.media_unread and (
            message.photo or
            message.video or
            is_voice_note(message)
        )
    )
@ABH.on(events.NewMessage(func=lambda e: e.is_private and joker_unread_media(e)))
async def Reda(event):
    x = await try_forward(event, gidvar)
    if x:
        return
    sender = await event.get_sender()
    name = sender.first_name
    user_id = sender.id
    date_str = event.date.strftime("%Y-%m-%d")
    day_name = ABH_Asbo3.get(event.date.strftime("%A"), "غير معروف")
    caption = f"""**
♡ تم حفظ الذاتية بنجاح ✓
♡ أسم المرسل : [{name}](tg://user?id={user_id})
♡ تاريخ الذاتية : `{date_str}`
♡ أرسلت في يوم `{day_name}`
♡    ABH    ♡
**"""
    await getfromevent(event, caption=caption)
