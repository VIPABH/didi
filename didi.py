from telethon.tl.types import DocumentAttributeAudio  
from ABH import *  
from datetime import datetime
import asyncio
import re
import os
import time
import sys
import io
import base64
import json
import requests
import psutil  
import yt_dlp
import socket
import sqlite3

OWNER_ID = 1247061935  

# 🆔 تم تحديث أيدي مجموعة التخزين الخاصة بك بنجاح هنا
STORAGE_CHAT_ID = -1003707622012  

SONGS_DIR = "didi_songs"
DOWNLOADS_DIR = "didi_downloads"
DB_FILE = "didi_system.db"  

# حساب وقت تشغيل السكربت من لحظة الإقلاع (Ultimate Stats Monitor)
START_TIME = datetime.now()

for folder in [SONGS_DIR, DOWNLOADS_DIR]:
    if not os.path.exists(folder): os.makedirs(folder)

try:
    with open("key.txt", "r", encoding="utf-8") as f: GEMINI_KEY = f.read().strip()
except FileNotFoundError: GEMINI_KEY = ""

ABH = TelegramClient('didi_user_ultra', API_ID, API_HASH)
is_active = True 
user_history = {}
spam_tracker = {}  
# 🎭 ذاكرة مؤقتة لحفظ بيانات حسابك الأصلي أثناء الانتحال
cloned_backup = {
    "first_name": "",
    "last_name": "",
    "pfp_path": None,
    "is_cloned": False
}
# --- 2. محرك قاعدة البيانات SQLite3 🗄️ ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS sudo_users (user_id INTEGER PRIMARY KEY, username TEXT, added_date TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS song_cache (file_key TEXT PRIMARY KEY, file_id TEXT, title TEXT)')
    conn.commit()
    conn.close()

def add_sudo_user(user_id, username=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO sudo_users VALUES (?, ?, ?)", (user_id, username, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def remove_sudo_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sudo_users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_user_allowed(user_id):
    if user_id == OWNER_ID: return True
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sudo_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_db_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT() FROM sudo_users")
    sudos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT() FROM song_cache")
    cached_songs = cursor.fetchone()[0]
    conn.close()
    return sudos, cached_songs

init_db()

# --- 3. محرك كاشف وتحليل الحسابات الوهمية والمحذوفة 🕵️‍♂️ ---
async def analyze_telegram_account(target_entity):
    """تحليل الحساب برمجياً لحساب نسبة الشبهة واكتشاف الحسابات الوهمية أو المحذوفة"""
    try:
        user = await ABH.get_entity(target_entity)
        
        # 1. فحص إذا كان الحساب محذوفاً نهائياً
        if getattr(user, 'deleted', False):
            return "❌ **حساب محذوف!**\nهذا الحساب تم حذفه بالكامل وتصفيته من سيرفرات التليجرام الافتراضية."
            
        score = 0
        reasons = []
        
        # 2. فحص التصنيفات الرسمية لشركة تليجرام
        if getattr(user, 'scam', False):
            score += 100
            reasons.append("- ⚠️ الحساب مصنف رسمياً كـ **نصاب (Scam)** من تليجرام.")
        if getattr(user, 'fake', False):
            score += 100
            reasons.append("- ⚠️ الحساب مصنف رسمياً كـ **وهمي (Fake)** من تليجرام.")
        if getattr(user, 'bot', False):
            score += 40
            reasons.append("- 🤖 الحساب عبارة عن بوت مبرمج وليس حساب مستخدم طبيعي.")
            
        # 3. فحص الخصائص المادية للحساب الجانبي
        if not user.photo:
            score += 30
            reasons.append("- 🖼️ لا توجد صورة شخصية للحساب (No Profile Photo).")
        if not user.username:
            score += 25
            reasons.append("- 🏷️ الحساب بدون معرف عام/يوزر نيم (No Username).")
            
        # تحديد النتيجة العامة بناءً على مجموع النقاط
        if score == 0:
            status_text = "🟢 آمن ونظيف وطبيعي 100%"
        elif score <= 30:
            status_text = "🟡 حساب طبيعي (لكن معلوماته مخفية/شخصية)"
        elif score <= 60:
            status_text = "🟠 مشبوه (قد يكون حساباً وهمياً أو مؤقتاً)"
        else:
            status_text = "🔴 وهمي / حساب خطير جداً"

        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        report = (
            f"🕵️‍♂️ **تقرير فحص وتتبع الحساب الشخصي:**\n\n"
            f"👤 الاسم: `{full_name if full_name else 'بدون اسم'}`\n"
            f"🆔 الأيدي: `{user.id}`\n"
            f"🏷️ اليوزر: `@{user.username or 'لا يوجد'}`\n"
            f"📊 تقييم ديدي أمنيّاً: **{status_text}**\n"
            f"📈 مؤشر الشبهة الحالية: `{min(score, 100)}%`\n"
        )
        if reasons:
            report += "\n🔍 **المؤشرات المرصودة:**\n" + "\n".join(reasons)
        return report

    except Exception as e:
        return f"❌ تعذر فحص الحساب المعني برمجياً: `{e}`"

# --- 4. محرك الاستخبارات السيبرانية والأمن المتطور (OSINT) 🛡️ ---
def cyber_link_scanner(text):
    urls = re.findall(r'(https?://[^\s]+)', text)
    if not urls: return None
    danger_keywords = ["grabify", "iplogger", "free-vbucks", "login-telegram", "free-crypto", "phishing", "malware", "virus", "token-stealer"]
    for url in urls:
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in danger_keywords):
            return f"🚨 **تنبيه أمني عالي الخطورة!**\nالرابط يحتوي على مؤشرات اختراق (IP Logger / Phishing).\n🔗 الرابط: `{url}`"
        if url_lower.endswith(('.exe', '.bat', '.scr', '.vbs', '.apk')):
            return f"⚠️ **تنبيه تحميل مشبوه!**\nالملف قد يكون ضاراً بجهازك.\n🔗 الملف: `{os.path.basename(url_lower)}`"
    return None

def ip_lookup(ip_address):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10).json()
        if res.get("status") == "fail": return "❌ الأيبي غير صحيح أو غير موجود."
        return (
            f"🌐 **بيانات الأيبي المعني ({ip_address}):**\n\n"
            f"🏳️ الدولة: `{res.get('country')} ({res.get('countryCode')})`\n"
            f"📍 المدينة: `{res.get('city')}`\n"
            f"📡 الشركة المزودة (ISP): `{res.get('isp')}`\n"
            f"🗺️ الإحداثيات: `{res.get('lat')}, {res.get('lon')}`\n"
            f"⏰ التوقيت本地: `{res.get('timezone')}`"
        )
    except: return "⚠️ فشل الاتصال بقاعدة بيانات الأيبيات."

async def scan_ports(host, ports=[80, 443, 22, 21, 23, 8080]):
    open_ports = []
    loop = asyncio.get_event_loop()
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = await loop.run_in_executor(None, sock.connect_ex, (host, port))
            if result == 0: open_ports.append(str(port))
            sock.close()
        except: pass
    if open_ports: return f"🔍 **نتائج فحص البورتات لـ ({host}):**\n🔌 البورتات المفتوحة: `{', '.join(open_ports)}`"
    return f"🔍 **نتائج فحص البورتات لـ ({host}):**\n🔒 جميع البورتات الأساسية المفحوصة مغلقة."

async def osint_username_lookup(username):
    targets = {
        "GitHub": f"https://api.github.com/users/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Twitter/X": f"https://twitter.com/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Telegram": f"https://t.me/{username}"
    }
    results = []
    loop = asyncio.get_event_loop()
    for platform, url in targets.items():
        try:
            def check(): return requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            response = await loop.run_in_executor(None, check)
            if response.status_code == 200: results.append(f"🟢 {platform}: [موجود ومستعمل]({url})")
            elif response.status_code == 404: results.append(f"⚪ {platform}: غير موجود (متاح للإنشاء)")
            else: results.append(f"🟡 {platform}: فحص محجوب أو غير مؤكد")
        except: results.append(f"🔴 {platform}: فشل الاتصال")
    return f"🕵️‍♂️ **تقرير استخبارات المعرفات (OSINT) لـ (`{username}`):**\n\n" + "\n".join(results)

# --- 5. محرك الـ SysInfo والأداء 🖥️ ---
def get_system_status():
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram_usage = psutil.virtual_memory().percent
    total_size = 0
    song_count = 0
    if os.path.exists(SONGS_DIR):
        for f in os.listdir(SONGS_DIR):
            if os.path.isfile(os.path.join(SONGS_DIR, f)):
                total_size += os.path.getsize(os.path.join(SONGS_DIR, f))
                song_count += 1
    total_size_mb = round(total_size / (1024 * 1024), 2)
    sudos, cached_songs = get_db_stats()
    return (
        f"📊 **لوحة تحكم أداء ديدي والسيرفر:**\n\n"
        f"🖥️ استهلاك المعالج (CPU): `{cpu_usage}%`\n"
        f"🧠 استهلاك الذاكرة (RAM): `{ram_usage}%`\n"
        f"🎵 مجلد الأغاني محلياً: `{song_count} ملف`\n"
        f"💾 مساحة الأغاني المجرّدة: `{total_size_mb} MB`\n"
        f"🗄️ المطورين المضافين بقاعدة البيانات: `{sudos} مستخدم`\n"
        f"⚡ المعرفات المؤرشفة بقاعدة البيانات: `{cached_songs} رمز`\n"
        f"📡 الحالة العامة: `مستقر بالكامل وعالي الكفاءة 🚀`"
    )

# --- 5b. محرك الإحصائيات المتقدمة والرادار (Ultimate Stats Monitor) 📡 ---
async def get_advanced_radar_stats(ABH):
    uptime = datetime.now() - START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        uptime_str = f"{days} يوم و {hours} ساعة"
    else:
        uptime_str = f"{hours} ساعة و {minutes} دقيقة و {seconds} ثانية"

    private_chats = 0
    groups = 0
    channels = 0
    unread_chats = 0
    
    try:
        async for dialog in ABH.iter_dialogs(limit=200):
            if dialog.is_user: private_chats += 1
            elif dialog.is_group: groups += 1
            elif dialog.is_channel: channels += 1
            if dialog.unread_count > 0: unread_chats += 1
    except: pass

    try:
        from telethon.tl.functions.contacts import GetBlockedRequest
        blocked = await ABH(GetBlockedRequest(offset=0, limit=1))
        blocked_count = blocked.count
    except: blocked_count = 0

    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram_usage = psutil.virtual_memory().percent

    report = (
        f"📊 **رادار ديدي - لوحة الإحصائيات الحية المتقدمة:**\n\n"
        f"⏱️ **وقت تشغيل السكربت:** `{uptime_str}`\n"
        f"🚫 **عدد الحسابات المحظورة (Block):** `{blocked_count} حساب`\n"
        f"📩 **المحادثات غير المقروءة حالياً:** `{unread_chats}`\n\n"
        f"🗂️ **تحليل الرادار لآخر 200 محادثة نشطة:**\n"
        f"👤 الخاص (Private): `{private_chats}`\n"
        f"👥 المجموعات (Groups): `{groups}`\n"
        f"📢 القنوات (Channels): `{channels}`\n\n"
        f"⚙️ **مؤشرات النظام والأداء:**\n"
        f"🖥️ استهلاك المعالج: `{cpu_usage}%` | الذاكرة: `{ram_usage}%`\n\n"
        f"📡 **الحالة:** مستقر والرد الذكي يراقب الأجواء! ⚡"
    )
    return report

# --- 6. محرك الذكاء الاصطناعي (Gemini) مع التوقيت الحي ---
def ask_gemini_balanced(user_id, prompt, image_path=None):
    if not GEMINI_KEY or GEMINI_KEY == "": return "⚠️ ملف key.txt فارغ!"
    current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    contents = []
    if image_path:
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
            contents.append({"role": "user", "parts": [{"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}}]})
        
    system_instruction = f"أنت ديدي (DIDI)، مساعد ذكي مدمج داخل الحساب الشخصي للمطور، خبير سيبراني ومبرمج محنك. تجيب باختصار ذكي وتطرح الخلاصة مباشرة بلهجة عراقية واثقة وفخمة. لمعلوماتك التاريخ والوقت الحالي بجهازك هو: {current_time_str}."
    
    if user_id not in user_history:
        user_history[user_id] = [
            {"role": "user", "parts": [{"text": system_instruction}]},
            {"role": "model", "parts": [{"text": "صار معلوم يا بطل! تم تفعيل الطور السريع والمختصر والتوقيت الحي شغال!"}]}
        ]
    else: user_history[user_id][0]["parts"][0]["text"] = system_instruction

    user_history[user_id].append({"role": "user", "parts": [{"text": prompt}]})
    if len(user_history[user_id]) > 15: user_history[user_id] = user_history[user_id][-15:]
    for hist in user_history[user_id]: contents.append(hist)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    try:
        response = requests.post(url, json={"contents": contents, "generationConfig": {"temperature": 0.6, "maxOutputTokens": 2048}}, timeout=30).json()
        answer = response['candidates'][0]['content']['parts'][0]['text']
        user_history[user_id].append({"role": "model", "parts": [{"text": answer}]})
        return answer
    except: return "⚠️ حدث خطأ داخلي أثناء معالجة الطلب."

# --- 7. محرك تحميل الأغاني والميديا الشامل 🎵🎬 ---
def find_local_or_download_song(song_name):
    clean_name = song_name.strip().lower()
    for file in os.listdir(SONGS_DIR):
        if file.lower().endswith(('.mp3', '.m4a')):
            file_base = os.path.splitext(file)[0].lower()
            if clean_name in file_base or file_base in clean_name: return os.path.join(SONGS_DIR, file)
                
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(SONGS_DIR, '%(title)s.%(ext)s'),
        'default_search': 'scsearch1', 
        'noplaylist': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([song_name])
        for file in os.listdir(SONGS_DIR):
            if file.lower().endswith('.mp3') and (clean_name in file.lower() or any(word in file.lower() for word in clean_name.split())):
                return os.path.join(SONGS_DIR, file)
        mp3_files = [os.path.join(SONGS_DIR, f) for f in os.listdir(SONGS_DIR) if f.endswith('.mp3')]
        if mp3_files: return max(mp3_files, key=os.path.getmtime)
    except: pass
    return None

async def download_universal_video(video_url):
    ydl_opts = {'format': 'best', 'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'), 'quiet': True, 'noplaylist': True}
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: await loop.run_in_executor(None, ydl.download, [video_url])
        video_files = [os.path.join(DOWNLOADS_DIR, f) for f in os.listdir(DOWNLOADS_DIR)]
        if video_files: return max(video_files, key=os.path.getmtime)
    except: pass
    return None

# --- 8. المعالج والمحاكي البرمجي لكود بايثون 💻 ---
async def execute_python(event, code):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirected_output, redirected_error = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = redirected_output, redirected_error
    stdout, stderr, exc = None, None, None
    try:
        local_vars = {"ABH": ABH, "event": event, "asyncio": asyncio, "os": os}
        exec(f"async def __ex(event):\n" + "".join(f"\n {l}" for l in code.split("\n")), {}, local_vars)
        await local_vars["__ex"](event)
    except Exception as e: exc = e
    finally: sys.stdout, sys.stderr = old_stdout, old_stderr
    stdout, stderr = redirected_output.getvalue(), redirected_error.getvalue()
    report = "💻 **تقرير المحاكي والمفسر البرمجي لـ بايثون:**\n\n"
    if exc: report += f"❌ **حدث خطأ بالبرمجة البرمجية:**\n`{exc}`\n"
    if stdout: report += f"📥 **المخرجات (Output):**\n```\n{stdout}\n```\n"
    if stderr: report += f"⚠️ **الأخطاء الجانبية (Stderr):**\n```\n{stderr}\n```\n"
    if not exc and not stdout and not stderr: report += "✅ تم تنفيذ الكود بنجاح بالخلفية وبدون مخرجات نصية!"
    await event.reply(report)

# --- 9. المعالج الأساسي المدمر بترتيب الأولويات الصارم 🎯 ---
@ABH.on(events.NewMessage())
async def handler(event):
    global is_active, spam_tracker, cloned_backup  # 💡 ضفناه هنا بالبداية تماماً
    if not event.text and not event.photo: return

    sender_id = event.sender_id
    raw_text = event.raw_text or ""

    # 🛡️ جدار حماية الجروبات الحية التلقائي (Anti-Spam)
    if event.is_group and sender_id != OWNER_ID:
        now = datetime.now()
        if sender_id not in spam_tracker: spam_tracker[sender_id] = []
        spam_tracker[sender_id] = [t for t in spam_tracker[sender_id] if (now - t).total_seconds() < 5]
        spam_tracker[sender_id].append(now)
        if len(spam_tracker[sender_id]) > 5:
            try:
                await event.delete()
                await event.respond(f"⚠️ **تنبيه حماية الجروب!**\nالمستخدم `[{sender_id}]` يسوي سبام مكثف، تم قمع رسالته تلقائياً! 🛡️")
                return
            except: pass

    # 🛑 جدار صلاحية التحكم بالـ Userbot
    if not is_user_allowed(sender_id): return

    # 🔍 الفحص السيبراني التلقائي للروابط في رسائلك الشخصية
    security_alert = cyber_link_scanner(raw_text)
    if security_alert: await event.reply(security_alert)

    # 📡 ميزة رادار كشف وتجميع بيانات الكروب الحالي
    if event.is_group and raw_text.strip() == "رادار":
        status_msg = await event.reply("📡 **جاري رصد وتجميع الإحداثيات الاستخباراتية للمجموعة...**")
        try:
            chat = await event.get_chat()
            chat_id = chat.id
            title = chat.title
            username = f"@{chat.username}" if getattr(chat, 'username', None) else "مجموعة خاصة"
            
            from telethon.tl.functions.channels import GetFullChannelRequest
            from telethon.tl.functions.messages import GetFullChatRequest
            from telethon.tl.types import Channel
            
            about = "لا يوجد وصف"
            members_count = "غير معروف"
            admins_count = "غير معروف"
            slowmode = "غير مفعّل"
            restricted_rights_text = "صلاحيات الأعضاء الافتراضية:\n"
            
            if isinstance(chat, Channel):
                full = await event.ABH(GetFullChannelRequest(chat))
                about = full.full_chat.about or "لا يوجد وصف"
                members_count = full.full_chat.participants_count or "غير معروف"
                admins_count = full.full_chat.admins_count or "غير معروف"
                slowmode = f"{full.full_chat.slowmode_seconds} ثانية" if full.full_chat.slowmode_seconds else "غير مفعّل"
                
                rights = chat.default_banned_rights
                if rights:
                    r_list = []
                    r_list.append("❌ الرسائل" if rights.send_messages else "✅ الرسائل")
                    r_list.append("❌ الوسائط" if rights.send_media else "✅ الوسائط")
                    r_list.append("❌ الملصقات" if rights.send_stickers else "✅ الملصقات")
                    r_list.append("❌ التثبيت" if rights.pin_messages else "✅ التثبيت")
                    r_list.append("❌ الإضافة" if rights.invite_users else "✅ الإضافة")
                    restricted_rights_text += " | ".join(r_list)
                else:
                    restricted_rights_text += "🔓 مفتوحة بالكامل (كل الصلاحيات متاحة)"
            else:
                full = await event.ABH(GetFullChatRequest(chat_id))
                members_count = len(full.full_chat.users)
                restricted_rights_text += "🔓 مفتوحة بالكامل (مجموعة عادية)"

            status_flags = []
            if getattr(chat, 'verified', False): status_flags.append("🟢 موثق")
            if getattr(chat, 'scam', False): status_flags.append("⚠️ نصب (Scam)")
            if getattr(chat, 'fake', False): status_flags.append("⚠️ وهمي (Fake)")
            if not status_flags: status_flags.append("⚪ غير مصنف")
            
            role = "عضو طبيعي"
            if getattr(chat, 'creator', False): role = "المالك الأساسي 👑"
            elif getattr(chat, 'admin_rights', None): role = "مشرف (Admin) 🛠️"

            report = (
                f"📡 **رادار كشف وتجميع بيانات المجموعة:**\n\n"
                f"👥 **الاسم:** `{title}`\n"
                f"🆔 **الأيدي:** `{chat_id}`\n"
                f"🏷️ **المعرف:** `{username}`\n"
                f"📝 **الوصف:**\n`{about}`\n\n"
                f"📊 **إحصائيات الأعضاء:**\n"
                f" ├ عدد الأعضاء: `{members_count}`\n"
                f" └ عدد المشرفين: `{admins_count}`\n\n"
                f"⚙️ **إعدادات وقيود الكروب:**\n"
                f" ├ رتبة ديدي هنا: **{role}**\n"
                f" ├ الوضع البطيء: `{slowmode}`\n"
                f" └ حالة الأمان: `{' | '.join(status_flags)}`\n\n"
                f"🛡️ **{restricted_rights_text}**"
            )
            await status_msg.edit(report)
        except Exception as e:
            await status_msg.edit(f"❌ **فشل رادار الكروب:** حدث خطأ أثناء جلب البيانات.\nالخطأ: `{e}`")
        return

    # 🖥️ أوامر أدوات النظام المباشرة والسريعة
    if raw_text in ["ديدي وضعك", "ديدي السيرفر", "ديدي النظام"]:
        await event.reply(get_system_status())
        return

    # تشغيل ميزة الرادار ولوحة الإحصائيات المتقدمة (Ultimate Stats Monitor)
    if raw_text in ["ديدي رادار", "ديدي احصائيات"]:
        status_msg = await event.reply("📡 **جاري فحص مؤشرات الرادار الحية وحساب البيانات... ثواني**")
        report = await get_advanced_radar_stats(event.ABH)
        await status_msg.edit(report)
        return
        
    if raw_text == "ديدي صفر الكاش":
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DELETE FROM song_cache")
        conn.commit(); conn.close()
        await event.reply("🗑️ تم تصفير الكاش المؤرشف بداخل قاعدة البيانات بنجاح!")
        return

    # 🕵️‍♂️ تنفيذ أمر كاشف الحسابات الوهمية / المحذوفة
    if raw_text.startswith("ديدي فحص حساب"):
        target = None
        reply_msg = await event.get_reply_message()
        
        # إذا تم استخدام الأمر بالرد على رسالة شخص
        if reply_msg:
            target = reply_msg.sender_id
        else:
            # استخراج اليوزر نيم أو الأيدي المكتوب بعد الأمر
            cmd_args = raw_text.replace("ديدي فحص حساب", "").strip()
            if cmd_args:
                target = cmd_args
                
        if target:
            status_msg = await event.reply("🔍 جاري فحص الحساب جيو-سيبرانياً وحساب مؤشرات الشبهة...")
            report = await analyze_telegram_account(target)
            await status_msg.edit(report)
        else:
            await event.reply("⚠️ يرجى استخدام الأمر بالرد على رسالة الشخص، أو كتابة اليوزر نيم/الأيدي بعد الأمر (مثال: `ديدي فحص حساب @username`).")
        return

    # 🌐 أدوات فحص الـ OSINT المرنة بالـ Regex
    if re.search(r'(?:افحص|فحص)\s+(?:الأيبي|الايب|ايبي|ايب)\s+([\d\.]+)', raw_text, flags=re.IGNORECASE):
        target_ip = re.search(r'(?:افحص|فحص)\s+(?:الأيبي|الايب|ايبي|ايب)\s+([\d\.]+)', raw_text, flags=re.IGNORECASE).group(1)
        await event.reply(ip_lookup(target_ip.strip()))
        return

    if re.search(r'(?:افحص|فحص)\s+بورتات\s+([^\s]+)', raw_text, flags=re.IGNORECASE):
        target_host = re.search(r'(?:افحص|فحص)\s+بورتات\s+([^\s]+)', raw_text, flags=re.IGNORECASE).group(1)
        status_msg = await event.reply("⚡ جاري فحص البورتات الأساسية سبرانياً، ثواني...")
        report = await scan_ports(target_host.strip())
        await status_msg.edit(report)
        return

    if raw_text.startswith("ديدي فحص يوزر "):
        target_user = raw_text.replace("ديدي فحص يوزر ", "").strip()
        status_msg = await event.reply("🕵️‍♂️ جاري تتبع وفحص المعرف الاستخباراتي عبر المنصات العالمية...")
        report = await osint_username_lookup(target_user)
        await status_msg.edit(report, link_preview=False)
        return

    # 📦 ميزة التخزين السريع والمستودع الخاص مع التقرير الاستخباراتي الدقيق للرسالة والمرسل
    if raw_text.strip() == "وك":
        reply_msg = await event.get_reply_message()
        if reply_msg:
            try:
                # 1. توجيه الرسالة الأصلية بأمان للحفاظ على جودتها ومحتواها
                forwarded = await ABH.forward_messages(STORAGE_CHAT_ID, reply_msg)
                forwarded_id = forwarded[0].id if isinstance(forwarded, list) else forwarded.id
                
                # 2. استخراج بيانات دقيقة ومعمقة عن المرسل والمصدر
                sender = await reply_msg.get_sender()
                chat = await reply_msg.get_chat()
                
                sender_name = "غير معروف"
                sender_uid = "لا يوجد"
                sender_username = "لا يوجد"
                
                if sender:
                    sender_uid = sender.id
                    if hasattr(sender, 'first_name'):
                        sender_name = f"{sender.first_name or ''} {getattr(sender, 'last_name', '') or ''}".strip()
                    elif hasattr(sender, 'title'):
                        sender_name = sender.title
                    sender_username = f"@{sender.username}" if getattr(sender, 'username', None) else "لا يوجد"
                
                chat_title = "محادثة خاصة (DM)"
                chat_cid = reply_msg.chat_id
                chat_username = "لا يوجد"
                msg_link = "لا يوجد"
                
                if chat:
                    chat_cid = chat.id
                    chat_title = getattr(chat, 'title', 'محادثة خاصة')
                    if getattr(chat, 'username', None):
                        chat_username = f"@{chat.username}"
                        msg_link = f"https://t.me/{chat.username}/{reply_msg.id}"
                
                msg_date = reply_msg.date.strftime("%Y-%m-%d %I:%M:%S %p")
                
                # 3. بناء تقرير البيانات التفصيلي
                info_report = (
                    f"📋 **تقرير ديدي الاستخباراتي للرسالة المخزنة:**\n\n"
                    f"👤 **بيانات المرسل (Sender Info):**\n"
                    f" ├ الاسم: `{sender_name}`\n"
                    f" ├ الأيدي: `{sender_uid}`\n"
                    f" └ المعرف: `{sender_username}`\n\n"
                    f"🧱 **بيانات مصدر الرسالة (Source Info):**\n"
                    f" ├ اسم المكان: `{chat_title}`\n"
                    f" ├ أيدي المحادثة: `{chat_cid}`\n"
                    f" └ معرف المحادثة: `{chat_username}`\n\n"
                    f"⏱️ **تفاصيل الرسالة والسجل الزمنّي:**\n"
                    f" ├ أيدي الرسالة: `{reply_msg.id}`\n"
                    f" ├ التوقيت الحي: `{msg_date}`\n"
                    f" └ رابط التوجيه: {msg_link if msg_link != 'لا يوجد' else '`مجموعة خاصة أو خاص`'}\n"
                )
                
                # إرسال التقرير بالرد على الرسالة الموجهة داخل المستودع لربط الملفات ببياناتها
                await ABH.send_message(STORAGE_CHAT_ID, info_report, reply_to=forwarded_id)
                await event.reply("📦")
            except Exception as e:
                await event.reply(f"❌ **فشل التخزين:** تأكد من إعدادات سطر 24 وصلاحيات الكروب.\nالخطأ البرمجي: `{e}`")
        else:
            await event.reply("⚠️ **تنبيه:** يرجى استخدام أمر `تخزين` بالرد (Reply) مباشرةً على الرسالة التي تريد حفظها!")
        return
# 🎭 ميزة الانتحال اليدوي (Clone Target)
    if raw_text.strip() == "انتحال":
        reply_msg = await event.get_reply_message()
        if not reply_msg:
            await event.reply("⚠️ **تنبيه:** يرجى الرد (Reply) على رسالة الشخص اللي تريد تنتحل شخصيته!")
            return

        status_msg = await event.reply("🎭 **جاري قنص الهوية البصرية والاسم للضحية...**")
        try:
            from telethon.tl.functions.account import UpdateProfileRequest
            from telethon.tl.functions.photos import UploadProfilePhotoRequest

            # 1. جلب بيانات الشخص المستهدف (الضحية)
            target_user = await ABH.get_entity(reply_msg.sender_id)
            target_first = target_user.first_name or ""
            target_last = target_user.last_name or ""

            # 2. أخذ نسخة احتياطية من معلوماتك الأصلية (فقط إذا لم تكن منتحلاً لشخص آخر بالفعل)
            if not cloned_backup["is_cloned"]:
                me = await ABH.get_me()
                cloned_backup["first_name"] = me.first_name or ""
                cloned_backup["last_name"] = me.last_name or ""
                
                # تحميل صورتك الشخصية الأصلية لحفظها بالسيرفر كـ Backup
                my_pfp_file = f"my_backup_pfp_{me.id}.jpg"
                cloned_backup["pfp_path"] = await ABH.download_profile_photo("me", file=my_pfp_file)
                cloned_backup["is_cloned"] = True

            # 3. تحميل صورة الضحية مؤقتاً لتطبيقها
            target_pfp_file = f"target_pfp_{target_user.id}.jpg"
            target_photo_path = await ABH.download_profile_photo(target_user.id, file=target_pfp_file)

            # 4. تطبيق هوية الضحية على حسابك
            await ABH(UpdateProfileRequest(first_name=target_first, last_name=target_last))
            
            # رفع صورة الضحية كصورة شخصية لك (إذا كان يملك صورة)
            if target_photo_path and os.path.exists(target_photo_path):
                uploaded_target_photo = await ABH.upload_file(target_photo_path)
                await ABH(UploadProfilePhotoRequest(file=uploaded_target_photo))
                os.remove(target_photo_path) # حذف صورة الضحية فوراً بعد الرفع
                
            await status_msg.edit(f"👤 **تم انتحال شخصية [{target_first}] بنجاح!**\n⏱️ ستبقى متخفياً بهويته حتى تكتب كلمة **'رجع'** في أي شات.")
            
        except Exception as e:
            await status_msg.edit(f"❌ **فشل الانتحال:** حدث خطأ أثناء تغيير بيانات الحساب.\nالخطأ: `{e}`")
        return

# 🔄 ميزة إنهاء الانتحال واسترجاع الحساب الأصلي
    if raw_text.strip() == "رجع":
        if not cloned_backup["is_cloned"]:
            await event.reply("⚠️ **تنبيه:** حسابك طبيعي بالكامل، لست في وضع الانتحال حالياً!")
            return

        status_msg = await event.reply("🔄 **جاري استعادة هويتك الأصلية وحذف آثار الانتحال...**")
        try:
            from telethon.tl.functions.account import UpdateProfileRequest
            from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest

            # 1. استرجاع الاسم الأصلي المأخوذ من الذاكرة الاحتياطية مالتك
            await ABH(UpdateProfileRequest(
                first_name=cloned_backup["first_name"], 
                last_name=cloned_backup["last_name"]
            ))

            # 2. حذف صورة الضحية الحالية لتقوم تليجرام تلقائياً بإظهار صورتك الأصلية التي تحتها
            my_photos = await ABH(GetUserPhotosRequest(user_id="me", offset=0, limit=1, max_id=0))
            if my_photos.photos:
                await ABH(DeletePhotosRequest(id=[my_photos.photos[0]]))

            # حذف ملف الصورة المؤقتة من جهازك علمود ما يترس مساحة
            if cloned_backup["pfp_path"] and os.path.exists(cloned_backup["pfp_path"]):
                os.remove(cloned_backup["pfp_path"]) 

            # 3. تصفير الذاكرة وإعادة تعيين وضع الانتحال إلى False
            cloned_backup["first_name"] = ""
            cloned_backup["last_name"] = ""
            cloned_backup["pfp_path"] = None
            cloned_backup["is_cloned"] = False

            await status_msg.edit("✅ **تم استرجاع حسابك الأصلي بنجاح!** ونظف ألبوم الصور بالكامل بدون أي تكرار.")
        except Exception as e:
            await status_msg.edit(f"❌ **فشل استرجاع الحساب الأصلي:** `{e}`")
        return
    # 🎬 محرك سحب ريلز وفيديوهات السوشيال ميديا التلقائي
    if raw_text.startswith("ديدي حمل ") or (any(keyword in raw_text for keyword in ["tiktok.com", "instagram.com/reel", "youtube.com/shorts"]) and sender_id == OWNER_ID):
        url_match = re.search(r'(https?://[^\s]+)', raw_text)
        if url_match:
            video_url = url_match.group(1)
            status_msg = await event.reply("🎬 **جاري قنص وتحميل الفيديو بأعلى دقة، ثواني...**")
            async with ABH.action(event.chat_id, 'video'):
                video_file = await download_universal_video(video_url)
                if video_file and os.path.exists(video_file):
                    await ABH.send_file(event.chat_id, video_file, caption="📥 **تم سحب وتحميل الفيديو بنجاح بواسطة ديدي الفتاك!**", reply_to=event.reply_to_msg_id)
                    os.remove(video_file)
                    await status_msg.delete()
                else:
                    await status_msg.edit("⚠️ فشل تحميل الفيديو، تأكد من صحة الرابط أو جرب لاحقاً.")
        return
# 🔍 ميزة مستخرج البيانات المخفية (Metadata Extractor)
    if raw_text.strip() == "فحص":
        reply_msg = await event.get_reply_message()
        if not reply_msg or not reply_msg.media:
            await event.reply("⚠️ **تنبيه:** يرجى الرد بكلمة `فحص` على صورة (أرسلها كملف لضمان بقاء البيانات) أو أي ملف آخر!")
            return

        status_msg = await event.reply("🔍 **جاري تحميل الملف وفحص البيانات المخفية (EXIF)...**")
        
        try:
            
            # 1. تحميل الملف مؤقتاً في سيرفر البوت
            temp_file_path = await ABH.download_media(reply_msg)
            if not temp_file_path:
                await status_msg.edit("❌ فشل تحميل الملف من خوادم تليجرام.")
                return

            metadata_text = f"📂 **معلومات الملف الأساسية:**\n"
            file_size = os.path.getsize(temp_file_path) / (1024 * 1024) # حساب الحجم بالميغابايت
            file_name = os.path.basename(temp_file_path)
            file_ext = os.path.splitext(temp_file_path)[1].lower()
            
            metadata_text += f"▪️ **اسم الملف:** `{file_name}`\n"
            metadata_text += f"▪️ **حجم الملف:** `{file_size:.2f} MB`\n"
            metadata_text += f"▪️ **الامتداد الفعلي:** `{file_ext}`\n\n"

            # 2. إذا كان الملف صورة، نفحص بيانات الـ EXIF والـ GPS
            if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.webp']:
                try:
                    from PIL import Image
                    from PIL.ExifTags import TAGS, GPSTAGS

                    exif_data = None
                    gps_info = {}
                    readable_exif = {}
                    width, height = 0, 0

                    # 💡 الحل هنا: نفتح الصورة داخل with لضمان إغلاق الملف وتحريره فوراً بعد القراءة
                    with Image.open(temp_file_path) as img:
                        exif_data = img._getexif()
                        width, height = img.size # حفظ الأبعاد قبل إغلاق الملف

                    if exif_data:
                        metadata_text += "📸 **بيانات الكاميرا والتصوير (EXIF):**\n"

                        # تفكيك وتصفية وسوم البيانات المخفية
                        for tag, value in exif_data.items():
                            decoded = TAGS.get(tag, tag)
                            readable_exif[decoded] = value
                            if decoded == "GPSInfo":
                                for g_tag, g_val in value.items():
                                    gps_decoded = GPSTAGS.get(g_tag, g_tag)
                                    gps_info[gps_decoded] = g_val

                        # استخراج تفاصيل الكاميرا والجهاز والوقت
                        camera_make = readable_exif.get("Make", "غير متوفر")
                        camera_model = readable_exif.get("Model", "غير متوفر")
                        date_time = readable_exif.get("DateTime", "غير متوفر")
                        software = readable_exif.get("Software", "غير متوفر")

                        metadata_text += f"▪️ **الشركة المصنعة:** `{camera_make}`\n"
                        metadata_text += f"▪️ **موديل الجهاز:** `{camera_model}`\n"
                        metadata_text += f"▪️ **تاريخ ووقت الالتقاط:** `{date_time}`\n"
                        metadata_text += f"▪️ **أبعاد الصورة:** `{width}x{height} بكسل`\n"
                        metadata_text += f"▪️ **نظام/برنامج التعديل:** `{software}`\n\n"

                        # استخراج وتحليل إحداثيات الموقع الجغرافي (GPS OSINT)
                        if gps_info:
                            try:
                                def to_decimal(gps_coords, ref):
                                    # دالة رياضية لتحويل الدرجات والدقائق والثواني إلى نظام عشري
                                    d = float(gps_coords[0])
                                    m = float(gps_coords[1]) / 60.0
                                    s = float(gps_coords[2]) / 3600.0
                                    if ref in ['S', 'W']:
                                        return -(d + m + s)
                                    return d + m + s

                                lat_data = gps_info.get("GPSLatitude")
                                lat_ref = gps_info.get("GPSLatitudeRef")
                                lon_data = gps_info.get("GPSLongitude")
                                lon_ref = gps_info.get("GPSLongitudeRef")

                                if lat_data and lat_ref and lon_data and lon_ref:
                                    lat = to_decimal(lat_data, lat_ref)
                                    lon = to_decimal(lon_data, lon_ref)
                                    
                                    metadata_text += "📍 **الاستخبارات الجغرافية وموقع الالتقاط (GPS):**\n"
                                    metadata_text += f"▪️ **خط العرض (Latitude):** `{lat:.6f}`\n"
                                    metadata_text += f"▪️ **خط الطول (Longitude):** `{lon:.6f}`\n"
                                    metadata_text += f"🔗 **موقع الصورة الجغرافي:** [اضغط هنا لفتح خرائط Google](http://maps.google.com/maps?q={lat},{lon})\n\n"
                            except Exception as gps_err:
                                metadata_text += f"⚠️ **ملاحظة:** تم العثور على بيانات موقع GPS ولكن فشل تحليلها: `{gps_err}`\n\n"
                    else:
                        metadata_text += "ℹ️ **EXIF:** لا توجد بيانات تصوير مخفية (EXIF) في هذه الصورة.\n*(ملاحظة: تليجرام يحذف البيانات تلقائياً إذا أرسلت الصورة بشكل عادي، أرسلها كـ 'ملف/File' لتجنب ذلك)*.\n\n"
                except Exception as img_err:
                    metadata_text += f"⚠️ **خطأ أثناء محاولة تشريح الصورة:** `{img_err}`\n\n"
            else:
                metadata_text += "ℹ️ **ملاحظة:** هذا الملف ليس صورة مدعومة لاستخراج بيانات EXIF، تم عرض بيانات الحجم والنظام فقط.\n\n"

            # 3. تعديل الرسالة وعرض النتائج للمستخدم وحذف الملف المؤقت فوراً
            await status_msg.edit(metadata_text, link_preview=False)
            
            # الآن الحذف سيتم بنجاح لأن الملف مغلق تماماً!
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        except Exception as e:
            await status_msg.edit(f"❌ **فشل فحص الملف:** حدث خطأ غير متوقع.\nالخطأ: `{e}`")
            # التأكد من عدم ترك مخلفات في السيرفر في حال حدوث خطأ
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
        return
    # 💻 أمر المفسر والمحاكي البرمجي لبايثون (للمالك الأساسي حصراً)
    if sender_id == OWNER_ID and raw_text.startswith("ديدي نفذ\n"):
        python_code = raw_text.replace("ديدي نفذ\n", "").strip()
        await execute_python(event, python_code)
        return
# 📥 ميزة جلب المحتوى المقيد المطورة (ألبوم + شريط تقدم + معلومات دقيقة)
    if raw_text.startswith("جلب ") or raw_text.startswith("ديدي جلب "):
        raw_link = raw_text.split(maxsplit=1)[1].strip()
        status_msg = await event.reply("🔎 **جاري تحليل الرابط واستخراج كافة البيانات...**")
        
        temp_files = []  # قائمة لحفظ مسارات الملفات المؤقتة لتنظيفها لاحقاً
        fetched_msg = None
        
        # دالة مساعدة لتنسيق الحجم
        def format_bytes(size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} TB"

        # دالة شريط التقدم التفاعلي
        async def progress_bar(current, total, action_text, last_edit_time):
            now = time.time()
            if now - last_edit_time[0] < 3:  # التحديث كل 3 ثوانٍ تجنباً للـ FloodWait
                return
            last_edit_time[0] = now
            percentage = (current / total) * 100
            done = int(percentage // 10)
            bar = "█" * done + "░" * (10 - done)
            try:
                await status_msg.edit(
                    f"⏳ **{action_text}**\n\n"
                    f"[{bar}] `{percentage:.1f}%`\n"
                    f"📦 **الحجم:** `{format_bytes(current)} / {format_bytes(total)}`"
                )
            except Exception:
                pass

        try:
            # 1. تنظيف وتفكيك الرابط
            link = raw_link.split('?')[0].rstrip('/')
            parts = link.split('/')
            msg_id = int(parts[-1])
            
            # تحديد معرّف القناة/المجموعة (خاصة أو عامة)
            if "/c/" in link:
                c_index = parts.index("c")
                channel_id = int("-100" + parts[c_index + 1])
                entity = channel_id
            else:
                entity = parts[-2]
                
            # 2. جلب الرسالة المطلوبة من السيرفر
            fetched_msg = await ABH.get_messages(entity, ids=msg_id)
            
            if not fetched_msg:
                await status_msg.edit("❌ **لم يتم العثور على الرسالة! تأكد من أنك عضو في القناة/المجموعة.**")
                return

            # 3. استخراج البيانات والمعلومات الدقيقة (Metadata)
            date_str = fetched_msg.date.strftime("%Y-%m-%d %H:%M:%S") if fetched_msg.date else "غير معروف"
            views = getattr(fetched_msg, 'views', None)
            forwards = getattr(fetched_msg, 'forwards', None)
            
            meta_info = f"📊 **معلومات الرسالة الدقيقة:**\n"
            meta_info += f"🆔 **معرف الرسالة:** `{fetched_msg.id}`\n"
            meta_info += f"📅 **التاريخ والوقت:** `{date_str}`\n"
            if views is not None:
                meta_info += f"👁 **المشاهدات:** `{views}` | "
            if forwards is not None:
                meta_info += f"🔄 **التوجيهات:** `{forwards}`\n"
            else:
                meta_info += "\n"
            meta_info += "-----------------------------------\n"

            last_edit = [0]  # لتتبع وقت التحديث لشريط التقدم

            # 🟢 الحالة الأولى: الرسالة عبارة عن ألبوم (مجموعة صور/فيديوهات)
            if fetched_msg.grouped_id:
                await status_msg.edit("📦 **تم اكتشاف ألبوم ميديا! جاري تجميع كافة عناصر الألبوم...**")
                
                album_messages = []
                # البحث عن جميع الرسائل التي تحمل نفس معرّف الألبوم
                async for msg in ABH.iter_messages(entity, min_id=msg_id - 10, max_id=msg_id + 10):
                    if msg.grouped_id == fetched_msg.grouped_id:
                        album_messages.append(msg)
                
                album_messages.sort(key=lambda x: x.id)
                caption_text = None
                
                for idx, m in enumerate(album_messages, 1):
                    if m.text and not caption_text:
                        caption_text = m.text
                    
                    if m.media:
                        f_path = await ABH.download_media(
                            m, 
                            progress_callback=lambda c, t: progress_bar(c, t, f"تحميل ألبوم ({idx}/{len(album_messages)})", last_edit)
                        )
                        if f_path:
                            temp_files.append(f_path)
                
                full_caption = meta_info + (f"📝 **الوصف:**\n{caption_text}" if caption_text else "")
                
                await status_msg.edit("📤 **جاري رفع الألبوم بالكامل إليك...**")
                await ABH.send_file(
                    event.chat_id,
                    temp_files,
                    caption=full_caption,
                    reply_to=event.reply_to_msg_id
                )

            # 🟡 الحالة الثانية: ميديا فردية (صورة، فيديو، ملف، صوت)
            elif fetched_msg.media:
                await status_msg.edit("📥 **جاري تحميل الميديا...**")
                
                f_path = await ABH.download_media(
                    fetched_msg,
                    progress_callback=lambda c, t: progress_bar(c, t, "جاري التحميل من القناة", last_edit)
                )
                if f_path:
                    temp_files.append(f_path)
                    
                full_caption = meta_info + (f"📝 **النص الأصلي:**\n{fetched_msg.text}" if fetched_msg.text else "")
                
                last_edit[0] = 0  # تصفير عداد الوقت للرفع
                await ABH.send_file(
                    event.chat_id,
                    f_path,
                    caption=full_caption,
                    reply_to=event.reply_to_msg_id,
                    progress_callback=lambda c, t: progress_bar(c, t, "جاري الرفع إليك", last_edit)
                )

            # 🔵 الحالة الثالثة: رسالة نصية فقط
            elif fetched_msg.text:
                full_text = meta_info + f"📝 **النص الأصلي:**\n\n{fetched_msg.text}"
                await status_msg.edit(full_text)

            else:
                await status_msg.edit("⚠️ **الرسالة فارغة أو تحتوي على نوع محتوى غير مدعوم.**")

        except Exception as e:
            await status_msg.edit(f"❌ **حدث خطأ أثناء الجلب:** `{e}`\n\n💡 *تأكد من صحة الرابط وأنك مشترك بالقناة إذا كانت خاصة.*")
            
        finally:
            # تنظيف كافة الملفات المؤقتة من الموبايل/الحاسبة فوراً
            for f in temp_files:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
            try:
                if fetched_msg and fetched_msg.media:
                    await status_msg.delete()
            except Exception:
                pass
        returns
    # 🛠️ أوامر التحكم بالـ Sudo وإدارة الجروبات
    if sender_id == OWNER_ID:
        if raw_text.startswith("ديدي ضيف مطور "):
            parts = raw_text.replace("ديدي ضيف مطور ", "").strip().split()
            if parts and parts[0].isdigit():
                add_sudo_user(int(parts[0]), parts[1] if len(parts) > 1 else "")
                await event.reply(f"✅ تم تفويض الأيدي `[{parts[0]}]` وإضافته لقاعدة البيانات كـ Sudo User.")
                return
        if raw_text.startswith("ديدي احذف مطور "):
            target_sudo = raw_text.replace("ديدي احذف مطور ", "").strip()
            if target_sudo.isdigit():
                remove_sudo_user(int(target_sudo))
                await event.reply(f"🗑️ تم حذف الأيدي `[{target_sudo}]` من صلاحيات قاعدة البيانات.")
                return

    if event.is_group and raw_text.startswith("ديدي "):
        cmd_part = raw_text.replace("ديدي ", "").strip()
        reply_msg = await event.get_reply_message()
        if reply_msg:
            try:
                if cmd_part == "اطرده":
                    await ABH.kick_participant(event.chat_id, reply_msg.sender_id)
                    await event.reply("🚀 تم طرد المستخدم خارج المجموعة بنجاح!")
                    return
                if cmd_part == "احظره":
                    from telethon.tl.functions.channels import EditBannedRequest
                    from telethon.tl.types import ChatBannedRights
                    await ABH(EditBannedRequest(event.chat_id, reply_msg.sender_id, ChatBannedRights(until_date=None, view_messages=True)))
                    await event.reply("🔨 تم حظر وإقصاء المستخدم من المجموعة نهائياً!")
                    return
            except Exception as e:
                await event.reply(f"❌ فشل الإجراء الإداري: `{e}`")
                return

    # 🎯 فلتر نداء ديدي الإلزامي لباقي العمليات الذكية
    if not re.search(r'^(?:ديدي|شغل|اغني[هة]|اكتب)', raw_text, flags=re.IGNORECASE): return
    clean_text = raw_text.replace('ديدي', '').strip()

    if clean_text in ["اقطع", "مضيوف"]:
        is_active = False
        await event.reply("💤 تم إيقاف الردود الذكية.. ديدي في وضع الصامت هسة.")
        return 
    if clean_text == "انهض":
        is_active = True
        await event.reply("🚀 ديدي استيقظ وعاد للعمل والتفاعل!")
        return 
    if not is_active: return

    # ✨ ميزة المؤثرات والنصوص الحركية (Typewriter Mode)
    if raw_text.startswith("ديدي اكتب "):
        text_to_type = raw_text.replace("ديدي اكتب ", "").strip()
        if sender_id == OWNER_ID and event.out:
            current_text = ""
            for char in text_to_type:
                current_text += char
                if current_text.strip():
                    await event.edit(current_text + " ▒")
                    await asyncio.sleep(0.15)
            await event.edit(text_to_type)
        return

    # 🎵 قسم الأغاني المطور والمؤرشف بقاعدة البيانات
    if 'شغل' in raw_text or 'اغنية' in raw_text:
        song_name = raw_text.replace('ديدي', '').replace('شغل', '').replace('اغنية', '').strip()
        if not song_name: return
        
        status_msg = await event.reply("🔍 جاري الفحص بقاعدة البيانات والبحث محلياً وسحابياً...")
        async with ABH.action(event.chat_id, 'audio'):
            audio_file = find_local_or_download_song(song_name)
            if audio_file and os.path.exists(audio_file):
                file_key = os.path.basename(audio_file).lower()
                display_title = os.path.splitext(os.path.basename(audio_file))[0]
                caption_text = f"**🎧 استمتع ديديك**\n🎵 الأغنية: `{display_title}`"
                
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT file_id FROM song_cache WHERE file_key = ?", (file_key,))
                db_result = cursor.fetchone()
                
                if db_result:
                    await ABH.send_file(event.chat_id, db_result[0], caption=caption_text, reply_to=event.reply_to_msg_id)
                else:
                    try:
                        sent_msg = await ABH.send_file(
                            event.chat_id, audio_file, caption=caption_text, voice=False,
                            attributes=[DocumentAttributeAudio(duration=0, title=display_title, performer="DIDI Bot")],
                            reply_to=event.reply_to_msg_id 
                        )
                        if sent_msg and sent_msg.media and hasattr(sent_msg.media, 'document'):
                            cursor.execute("INSERT OR REPLACE INTO song_cache VALUES (?, ?, ?)", (file_key, str(sent_msg.media.document), display_title))
                            conn.commit()
                    except Exception as e: print(f"❌ خطأ بالرفع: {e}")
                conn.close()
                await status_msg.delete()
            else: await status_msg.edit(f"⚠️ تعذر العثور على الأغنية أو تحميلها.")
        return

    # 📸 قسم الصور والتحليل المرئي
    if event.photo:
        async with ABH.action(event.chat_id, 'typing'):
            img_path = await event.download_media()
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(None, ask_gemini_balanced, sender_id, clean_text if clean_text else "اشرح لي الصورة", img_path)
            await event.reply(answer)
            if os.path.exists(img_path): os.remove(img_path)
        return

    # 🧠 قسم الرد الذكي لـ جيميناي
    async with ABH.action(event.chat_id, 'typing'):
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(None, ask_gemini_balanced, sender_id, clean_text if clean_text else "هلا ديدي")
        await event.reply(answer)
# 🕵️‍♂️ ميزة التلصص المطورة لحفظ الميديا ذاتية التدمير (Ultra TTL Saver)
@ABH.on(events.NewMessage(incoming=True))
async def ultra_ttl_saver(event):
    # 1. التثبت من أن الرسالة خاصة وتحتوي على ميديا
    if not (event.is_private and event.media):
        return

    # 2. استخراج زمن التدمير الذاتي بجميع صياغاته البرمجية بالتلجرام
    media = event.media
    ttl_seconds = getattr(media, 'ttl_seconds', None) or getattr(event.message, 'ttl_period', None)

    # إذا لم تكن الميديا ذاتية التدمير، يتم تجنب معالجتها
    if not ttl_seconds:
        return

    file_path = None
    try:
        # 3. جلب تفاصيل المرسل بدقة عالية
        sender = await event.get_sender()
        if sender:
            first_name = getattr(sender, 'first_name', '') or ''
            last_name = getattr(sender, 'last_name', '') or ''
            sender_name = f"{first_name} {last_name}".strip() or "بدون اسم"
            username = f"@{sender.username}" if getattr(sender, 'username', None) else "لا يوجد"
            sender_id = sender.id
        else:
            sender_name = "غير معروف"
            username = "لا يوجد"
            sender_id = event.sender_id

        # 4. تحديد نوع الميديا المجلوبة
        from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
        media_type = "ميديا مؤقتة"
        
        if isinstance(media, MessageMediaPhoto):
            media_type = "📷 صورة ذاتية التدمير"
        elif isinstance(media, MessageMediaDocument):
            mime = getattr(media.document, 'mime_type', '')
            if mime.startswith('video/'):
                media_type = "🎥 فيديو ذاتي التدمير"
            elif mime.startswith('audio/'):
                media_type = "🎙 بصمة/صوت مؤقت"
            else:
                media_type = "📁 ملف/ميديا مؤقتة"

        # 5. تحميل الملف فوراً إلى الذاكرة
        file_path = await ABH.download_media(event.message)

        if file_path:
            # تجهيز التقرير التفصيلي
            caption = (
                f"🚨 **تم صيد {media_type} بنجاح!**\n\n"
                f"👤 **المرسل:** {sender_name}\n"
                f"🆔 **المعرف:** `{sender_id}` | {username}\n"
                f"⏱ **مدة التدمير:** `{ttl_seconds}` ثوانٍ\n"
                f"📅 **التاريخ:** `{event.date.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            )
            if event.text:
                caption += f"\n📝 **النص المرفق:**\n{event.text}"

            # 6. الإرسال إلى الرسائل المحفوظة
            await ABH.send_file(
                "me",
                file_path,
                caption=caption
            )
            
    except Exception as e:
        print(f"❌ خطأ أثناء صيد الميديا المؤقتة: {e}")
        
    finally:
        # 7. الضمان القطعي لحذف الملف المؤقت لتوفير المساحة
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
# --- 10. تشغيل السكربت الشامل ---
async def main():
    await ABH.start()
    print("🚀 ديدي جاهز هسة كـ Userbot أمني ومستقر بالكامل!")
    await ABH.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
