import asyncio, os, sys, io, yt_dlp
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

# --- [ تعريف وإنشاء مجلدات الحفظ تلقائياً ] ---
SONGS_DIR = "downloads/songs"
DOWNLOADS_DIR = "downloads/videos"
os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# --- 7. محرك تحميل الأغاني والميديا الشامل (مطور ومتوافق مع Async) 🎵🎬 ---
async def find_local_or_download_song(song_name):
    clean_name = song_name.strip().lower()
    
    # 1. البحث في الملفات المحلية أولاً لتوفير الوقت والبيانات
    for file in os.listdir(SONGS_DIR):
        if file.lower().endswith(('.mp3', '.m4a')):
            file_base = os.path.splitext(file)[0].lower()
            if clean_name in file_base or file_base in clean_name:
                return os.path.join(SONGS_DIR, file)
                
    # 2. إعدادات التحميل من ساوند كلاود أو يوتيوب
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(SONGS_DIR, '%(title)s.%(ext)s'),
        'default_search': 'scsearch1', 
        'noplaylist': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'quiet': True,
    }
    
    loop = asyncio.get_event_loop()
    try:
        # تشغيل التحميل في الخلفية لتجنب تجميد اليوزر بوت
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([song_name]))
            
        # البحث عن الملف المحمل وإرجاع مساره
        for file in os.listdir(SONGS_DIR):
            if file.lower().endswith('.mp3') and (clean_name in file.lower() or any(word in file.lower() for word in clean_name.split())):
                return os.path.join(SONGS_DIR, file)
                
        # في حال تغير الاسم بعد التحميل، نرجع أحدث ملف صوتي تم تعديله
        mp3_files = [os.path.join(SONGS_DIR, f) for f in os.listdir(SONGS_DIR) if f.endswith('.mp3')]
        if mp3_files:
            return max(mp3_files, key=os.path.getmtime)
    except Exception as e:
        pass
    return None

async def download_universal_video(video_url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True
    }
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([video_url]))
            
        video_files = [os.path.join(DOWNLOADS_DIR, f) for f in os.listdir(DOWNLOADS_DIR)]
        if video_files:
            return max(video_files, key=os.path.getmtime)
    except Exception as e:
        pass
    return None 
@ABH.on(events.NewMessage(pattern=r"^(?:غنية|اغنية|تحميل)\s+(.+)", outgoing=True))
async def song_command(event):
    song_name = event.pattern_match.group(1)
    await event.edit("🔍 **جاري البحث والتحميل...**")
    
    file_path = await find_local_or_download_song(song_name)
    
    if file_path:
        await event.edit("⬆️ **جاري رفع الملف الصوتي...**")
        await ABH.send_file(
            event.chat_id, 
            file_path, 
            caption=f"🎵 **{song_name}**",
            reply_to=event.reply_to_msg_id
        )
        await event.delete() # حذف رسالة الأمر بعد الإرسال
    else:
        await event.edit("❌ **عذراً، لم أتمكن من العثور على الأغنية.**")
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
