from telethon import events
import asyncio, sys, os
from UScode import *
from الاعدادات import *
from التخزين import *
from ذاتية import *
from الميمز import *
from بوتات import *
from didi import *
@ABH.on(events.NewMessage(pattern="^اطفاء$", from_users=[1910015590], outgoing=True))
async def shutdown(event):
    await event.reply("🔴 جارٍ إيقاف اليوزربوت ...")
    await asyncio.sleep(1)
    await ABH.disconnect()
    sys.exit(0)
@ABH.on(events.NewMessage(pattern="^رست$", from_users=[1910015590], outgoing=True))
async def resetbot(event):
    await asyncio.sleep(1)
    await restart_bot(event)
@ABH.on(events.NewMessage(pattern="^.حدث$", from_users=[1910015590], outgoing=True))
async def resetbot(event):
    await event.reply('يجري التحديث')
    await update_repo(event)
@ABH.on(events.NewMessage(pattern="^اعادة تشغيل$", incoming=True))
async def restart_bot(event):
    await event.respond("♻️ جارٍ إعادة تشغيل اليوزربوت ...")
    os.execv(sys.executable, [sys.executable, "run.py"])
async def run_cmd(command: str):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode
@ABH.on(events.NewMessage(pattern="^.تحديث$", outgoing=True))
async def update_repo(event):
    msg = await event.edit(" جاري جلب آخر التحديثات من الريبو عبر...")
    stdout, stderr, code = await run_cmd("git pull")
    if code == 0:
        await msg.edit(f" تحديث السورس بنجاح")
        os.execv(sys.executable, [sys.executable, "run.py"])
    else:
        await msg.edit(f" حدث خطأ أثناء التحديث:\n\n{stderr}")
async def main():
    await ABH.start()
    await ABH.run_until_disconnected()
if __name__ == "__main__":
    asyncio.run(main())
