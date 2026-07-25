from telethon.tl.functions.channels import CreateChannelRequest
from shortcuts import *  # type: ignore
from config import *  # type: ignore
from ABH import *  # type: ignore
import re, os, json
async def create_group(name, about):
    result = await ABH(CreateChannelRequest(title=name, about=about, megagroup=True))
    group = result.chats[0]
    return group.id, group.title
@ABH.on(events.NewMessage(pattern='/config', outgoing=True))
async def config_vars(event):
    global gidvar, hidvar
    config_file = "var.json"
    me = await ABH.get_me()
    async for msg in ABH.iter_messages(me.id):
        if not msg.text:
            continue
        gid_match = re.search(r'gidvar:\s*(.+)', msg.text, re.IGNORECASE)
        hid_match = re.search(r'hidvar:\s*(.+)', msg.text, re.IGNORECASE)
        session = re.search(r'Session String:\s*(.+)', msg.text, re.IGNORECASE)
        if gid_match and not gidvar:
            gidvar = gid_match.group(1).strip()
        if hid_match and not hidvar:
            hidvar = hid_match.group(1).strip()
        if gidvar and hidvar:
            break
    newly_created = []
    if not gidvar:
        gidvar, gid_name = await create_group("مجموعة التخزين", "هذه المجموعة مخصصة لتخزين البيانات.")
        newly_created.append(("مجموعة التخزين", gidvar))
    if not hidvar:
        hidvar, hid_name = await create_group("مجموعة الإشعارات", "هذه المجموعة مخصصة للتنبيهات.")
        newly_created.append(("مجموعة الإشعارات", hidvar))
    if newly_created:
        config_text = f'''فارات السورس
لا تحذف الرسالة للحفاظ على كروبات السورس
مجموعة التخزين gidvar: {gidvar}
مجموعة الإشعارات hidvar: {hidvar}
'''
        await ABH.send_message(me.id, config_text)
        ids_text = "تم إنشاء الكروبات التالية:\n\n"
        for title, gid in newly_created:
            ids_text += f"**{title}**\nID: `{gid}`\n\n"
        await ABH.send_message(me.id, ids_text)
    config_data = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError:
            config_data = {}
    config_data["gidvar"] = gidvar
    config_data["hidvar"] = hidvar
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def privte_save(event):
    if not gidvar or not hidvar:
        print("gidvar not found")
        await config_vars(event)
        return
    uid = event.sender_id
    s = await event.get_sender()
    if uid == 777000 or s.bot:
        return
    text = event.raw_text
    name = s.first_name or s.username or "Unknown"
    await ABH.send_message(
        int(gidvar), 
f'''المرسل : {name}

ايديه : `{uid}`

ارسل : {text}
''')
    m = event.message.id
    if not m:
        return
    await try_forward(event, gidvar)
@ABH.on(events.NewMessage(incoming=True, func=lambda e: e.mentioned))
async def group_save(event):
    if not gidvar or not hidvar:
        print("gidvar not found")
        await config_vars(event)
        return
    s = await event.get_sender()
    if s.bot:
        return
    gid = event.chat_id
    gid = str(gid).replace("-100", "").replace(" ", "")
    name = s.first_name or s.username or "Unknown"
    chat = await event.get_chat()
    chat_title = getattr(chat, "title", "محادثة خاصة")
    await ABH.send_message(
        int(gidvar),
f'''#التــاكــات

⌔┊الكــروب : {chat_title}

⌔┊المـرسـل :  {name}

⌔┊الرســالـه : {event.message.text}

⌔┊رابـط الرسـاله :  [link](https://t.me/c/{gid}/{event.message.id})
''')
    await try_forward(event, gidvar)
@ABH.on(events.NewMessage(pattern='^اضف كروب التخزين$', outgoing=True))
async def add_gidvar(event):
    r = await event.get_reply_message()
    if not r or not r.text or not r.text.startswith("-100"):
        await event.reply("❌ يجب الرد على رسالة تحتوي على آيدي يبدأ بـ -100")
        return
    gidvar = r.text.strip()
    config_data = {}
    if os.path.exists('var.json'):
        try:
            with open('var.json',"r",encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError:
            pass
    config_data["gidvar"] = gidvar
    with open('var.json',"w",encoding="utf-8") as f:
        json.dump(config_data,f,ensure_ascii=False,indent=4)
    await event.edit("✅ تم تعيين آيدي كروب التخزين بنجاح")
@ABH.on(events.NewMessage(pattern='^اضف كروب الاشعارات$', outgoing=True))
async def add_hidvar(event):
    r = await event.get_reply_message()
    if not r or not r.text or not r.text.startswith("-100"):
        await event.reply("❌ يجب الرد على رسالة تحتوي على آيدي يبدأ بـ -100")
        return
    hidvar = r.text.strip().replace("-100", "")
    config_data = {}
    if os.path.exists('var.json'):
        try:
            with open('var.json',"r",encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError:
            pass
    config_data["hidvar"] = hidvar
    with open('var.json',"w",encoding="utf-8") as f:
        json.dump(config_data,f,ensure_ascii=False,indent=4)
    await event.edit("✅ تم تعيين آيدي كروب الاشعارات بنجاح")
