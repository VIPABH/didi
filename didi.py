import asyncio, os, sys, io
from datetime import datetime
from telethon import events
from ABH import ABH  # استيراد العميل الصحيح من ملف الاتصال

# --- [ 1. المتغيرات العامة وقواعد البيانات المؤقتة ] ---
OWNER_ID = 1247061935  # ضع الأيدي الخاص بك هنا
is_active = True
spam_tracker = {}
cloned_backup = None

# --- [ 2. دوال التحقق المساعدة (Helper Functions) ] ---
def is_user_allowed(sender_id):
    # يمكنك إضافة قائمة بالمستخدمين المسموح لهم لاحقاً
    return sender_id == OWNER_ID

# --- [ 3. المعالج الأساسي الشامل (Master Handler) ] ---
@ABH.on(events.NewMessage())
async def master_handler(event):
    global is_active, spam_tracker, cloned_backup
    
    # تجاهل الرسائل الفارغة أو التي لا تحتوي على نص/وسائط مهمة
    if not event.text and not event.photo:
        return

    sender_id = event.sender_id
    raw_text = event.raw_text or ""

    # =================================================================
    # الأولوية رقم 1: الفحص السيبراني للروابط (يعمل على الجميع وحتى الغرباء!)
    # =================================================================
    if "http://" in raw_text or "https://" in raw_text:
        # ضع كود فحص الروابط المشبوهة هنا
        # إذا كان الرابط ملغماً: اعمل delete() + return فوراً
        pass

    # =================================================================
    # الأولوية رقم 2: جدار حماية الجروبات والـ Anti-Spam (لغير المالك)
    # =================================================================
    if event.is_group and sender_id != OWNER_ID:
        now = datetime.now()
        if sender_id not in spam_tracker:
            spam_tracker[sender_id] = []
        
        # تنظيف الطوابع الزمنية القديمة (أكثر من 5 ثوانٍ)
        spam_tracker[sender_id] = [t for t in spam_tracker[sender_id] if (now - t).total_seconds() < 5]
        spam_tracker[sender_id].append(now)

        # التحقق من المخالفة (إرسال التنبيه مرة واحدة فقط لتجنب الـ Flood)
        if len(spam_tracker[sender_id]) == 6:
            try:
                await event.delete()
                await event.respond(f"⚠️ **تنبيه حماية الجروب**\n[المستخدم](tg://user?id={sender_id}) يسوي سبام مكثف، تم قمع رسائله تلقائياً 🛡")
                return
            except: pass
        elif len(spam_tracker[sender_id]) > 6:
            try:
                await event.delete()  # حذف صامت للمخالفات المستمرة
                return
            except: pass

    # =================================================================
    # الأولوية رقم 3: جدار صلاحية التحكم باليوزر بوت (Userbot Authorization)
    # =================================================================
    # أي أمر برمجية تحت هذا السطر لن ينفذ إلا للمالك (أو المسموح لهم)
    if not is_user_allowed(sender_id):
        return

    # =================================================================
    # الأولوية رقم 4: أوامر التحكم والتنفيذ (Commands & Eval)
    # =================================================================
    
    # 🔹 أمر النسخ الاحتياطي (الباكاب)
    if raw_text.strip() in ["ديدي باكاب", "ديدي نسخة"]:
        try:
            await event.edit("🔄 **جاري تجهيز وإرسال النسخة الاحتياطية...**")
            # ضع كود الإرسال هنا وتذكر استخدام العميل ABH
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ:** `{str(e)}`")
        return

    # 🔹 أمر منفذ أكواد البايثون (Eval / Exec)
    if raw_text.startswith(".c ") or raw_text.startswith(".py "):
        code = raw_text.split(" ", 1)[1]
        await execute_python(event, code)
        return

# --- [ 4. محرك تنفيذ أكواد البايثون في الخلفية ] ---
async def execute_python(event, code):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirected_output, redirected_error = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = redirected_output, redirected_error
    stdout, stderr, exc = None, None, None
    
    try:
        local_vars = {"ABH": ABH, "event": event, "asyncio": asyncio, "os": os}
        exec(f"async def __ex(event):\n" + "\n".join(f"    {l}" for l in code.split("\n")), {}, local_vars)
        await local_vars["__ex"](event)
    except Exception as e:
        exc = e
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()
        
    report = "**💻 تقرير المحاكي والمفسر البرمجي لبايثون 💻**\n\n"
    if exc: report += f"❌ **حدث خطأ بالبرمجة:**\n`{exc}`\n\n"
    if stdout: report += f"💬 **المخرجات (Output):**\n`{stdout}`\n\n"
    if stderr: report += f"⚠️ **الأخطاء الجانبية (Stderr):**\n`{stderr}`\n\n"
    if not exc and not stdout and not stderr:
        report += "✅ *تم تنفيذ الكود بنجاح في الخلفية وبدون مخرجات نصية.*"
        
    await event.reply(report)
