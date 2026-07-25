from telethon.sessions import StringSession
from datetime import datetime
from telethon import events
from ABH import ABH
now = datetime.now()
تاريخ = now.strftime("%Y-%m-%d")
ساعة = now.strftime("%I:%M:%S %p")
وقت_بدء_التشغيل = datetime.now()
@ABH.on(events.NewMessage(pattern="^.فحص|فحص", outgoing=True))
async def testup(event):
    الآن = datetime.now()
    مدة = الآن - وقت_بدء_التشغيل
    الأيام = مدة.days
    الثواني = مدة.seconds
    الساعات = الثواني // 3600
    الدقائق = (الثواني % 3600) // 60
    باقي_الثواني = الثواني % 60
    مدة_التشغيل_المكتوبة = []
    if الأيام:
        مدة_التشغيل_المكتوبة.append(f"{الأيام} يوم")
    if الساعات:
        مدة_التشغيل_المكتوبة.append(f"{الساعات} ساعة")
    if الدقائق:
        مدة_التشغيل_المكتوبة.append(f"{الدقائق} دقيقة")
    if باقي_الثواني:
        مدة_التشغيل_المكتوبة.append(f"{باقي_الثواني} ثانية")
    مدة_التشغيل = "، ".join(مدة_التشغيل_المكتوبة) or "0 ثانية"
    التاريخ = الآن.strftime("%Y-%m-%d")
    الساعة = الآن.strftime("%I:%M:%S %p")
    start = datetime.now()
    await event.edit("**᯽︙ جـاري فـحص الـبـوت**")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    cap = (
        f"**᯽︙ السورس شغال**\n"
        f"᯽︙ **الـتـاريخ:** `{التاريخ}`\n"
        f"᯽︙ **الـسـاعه:** `{الساعة}`\n"
        f"᯽︙ **الـزمن:** `{ms} ms`\n"
        f"᯽︙ **شغال من:** `{مدة_التشغيل}`\n"
    )
    await event.delete()
    pic = 'https://files.catbox.moe/ebn0d8.jpg'
    await event.respond(file=pic, message=cap)
