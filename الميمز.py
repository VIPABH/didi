from ABH import ABH, events #type:ignore
@ABH.on(events.NewMessage(pattern='^اللهي$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/23"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^سيد$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/16"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^ايرور$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/7"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^نيو$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/5"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^انجب$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/79"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^ماذا$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/81"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^يولن$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/292"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^هه$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/338"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^لاا$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/535"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^مرهم$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/537"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^لتكفرونه$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/571"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^وخر$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/589"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^اش$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/592"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^انعل$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/597"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^طاح$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/612"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^لب$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/614"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^صل$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/735"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^فد$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/748"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^نعل$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1008"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^الماوارثها$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1093"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^يدكتور$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1107"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^نوكيا$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1111"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^امريكا$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1113"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^هاا$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1115"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^مي$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1116"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^ببج$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1134"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^فلا$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1160"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^تفف$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1161"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^شيله عبود$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1162"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^ههه$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1164"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^صلاة$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1187"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^زيج$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1206"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^الكعبة$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1207"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^هههاي$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1252"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^خل يأتي$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1253"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^هههه$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1254"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^محح$', outgoing=True))
async def meme(event):
    await event.delete()
    url = f"https://t.me/abhmeme/1255"
    r = await event.get_reply_message()
    if r is not None:
        await ABH.send_file(event.chat_id, url, reply_to=r.id)
    else:
        await ABH.send_file(event.chat_id, url)
@ABH.on(events.NewMessage(pattern='^الميمز$', outgoing=True))
async def list(event):
    await event.edit(
        '''᯽︙ قائمة تخزين اوامر الميمز:
البصمة : `اللهي`
البصمة : `سيد`
البصمة : `ايرور`
البصمة : `نيو`
البصمة : `انجب`
البصمة : `ماذا`
البصمة : `يولن`
البصمة : `هه`
البصمة : `لاا`
البصمة : `مرهم`
البصمة : `لتكفرونه`
البصمة : `وخر`
البصمة : `اش`
البصمة : `انعل`
البصمة : `طاح`
البصمة : `لب`
البصمة : `صل`
البصمة : `فد`
البصمة : `نعل`
البصمة : `الماوارثها`
البصمة : `يدكتور`
البصمة : `امريكا`
البصمة : `هاا`
البصمة : `مي`
البصمة : `ببج`
البصمة : `فلا`
البصمة : `تف`
البصمة : `شيله عبود`
البصمة : `ههه`
البصمة : `صلاة`
البصمة : `زيج`
البصمة : `الكعبة`
البصمة : `خل يأتي`
البصمة : `هههه`
البصمة : `محح`
''')
