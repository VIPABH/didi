import asyncio, os, sys, io, yt_dlp, sqlite3, re
from datetime import datetime
from telethon import events
from ABH import ABH 

# --- [ 1. المتغيرات العامة وقواعد البيانات المؤقتة ] ---
OWNER_ID = 1247061935  # ضع الأيدي الخاص بك هنا
is_active = True
spam_tracker = {}
cloned_backup = None
# ضيف هذا المتغير ببداية الملف حتى يحفظ معلوماتك الأصلية
cloned_backup = {
    "is_cloned": False,
    "first_name": "",
    "last_name": "",
    "pfp_path": None
}
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

@ABH.on(events.NewMessage(outgoing=True, pattern=r"^(انتحال|رجع)$"))
async def clone_and_revert_handler(event):
    import os
    command = event.raw_text.strip()
    
    # 🎭 ميزة الانتحال اليدوي (Clone Target)
    if command == "انتحال":
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

            # 2. أخذ نسخة احتياطية من معلوماتك الأصلية
            if not cloned_backup["is_cloned"]:
                me = await ABH.get_me()
                cloned_backup["first_name"] = me.first_name or ""
                cloned_backup["last_name"] = me.last_name or ""
                cloned_backup["is_cloned"] = True

            # 3. تحميل صورة الضحية مؤقتاً لتطبيقها
            target_pfp_file = f"target_pfp_{target_user.id}.jpg"
            target_photo_path = await ABH.download_profile_photo(target_user.id, file=target_pfp_file)

            # 4. تطبيق هوية الضحية على حسابك
            await ABH(UpdateProfileRequest(first_name=target_first, last_name=target_last))
            
            # رفع صورة الضحية كصورة شخصية لك
            if target_photo_path and os.path.exists(target_photo_path):
                uploaded_target_photo = await ABH.upload_file(target_photo_path)
                await ABH(UploadProfilePhotoRequest(file=uploaded_target_photo))
                os.remove(target_photo_path)
                
            await status_msg.edit(f"👤 **تم انتحال شخصية [{target_first}] بنجاح!**\n⏱️ ستبقى متخفياً بهويته حتى تكتب كلمة **'رجع'** في أي شات.")
            
        except Exception as e:
            await status_msg.edit(f"❌ **فشل الانتحال:** حدث خطأ أثناء تغيير بيانات الحساب.\nالخطأ: `{e}`")
        return

    # 🔄 ميزة إنهاء الانتحال واسترجاع الحساب الأصلي
    elif command == "رجع":
        if not cloned_backup["is_cloned"]:
            await event.reply("⚠️ **تنبيه:** حسابك طبيعي بالكامل، لست في وضع الانتحال حالياً!")
            return

        status_msg = await event.reply("🔄 **جاري استعادة هويتك الأصلية وحذف آثار الانتحال...**")
        try:
            from telethon.tl.functions.account import UpdateProfileRequest
            from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest

            # 1. استرجاع الاسم الأصلي
            await ABH(UpdateProfileRequest(
                first_name=cloned_backup["first_name"], 
                last_name=cloned_backup["last_name"]
            ))

            # 2. حذف صورة الضحية لاسترجاع صورتك الأساسية تحتها
            my_photos = await ABH(GetUserPhotosRequest(user_id="me", offset=0, limit=1, max_id=0))
            if my_photos.photos:
                await ABH(DeletePhotosRequest(id=[my_photos.photos[0]]))

            # 3. تصفير الذاكرة
            cloned_backup["first_name"] = ""
            cloned_backup["last_name"] = ""
            cloned_backup["is_cloned"] = False

            await status_msg.edit("✅ **تم استرجاع حسابك الأصلي بنجاح!** ونظف ألبوم الصور بالكامل بدون أي تكرار.")
        except Exception as e:
            await status_msg.edit(f"❌ **فشل استرجاع الحساب الأصلي:** `{e}`")
        return

# 📥 ميزة جلب المحتوى المقيد المطورة (ألبوم + شريط تقدم + معلومات دقيقة)
@ABH.on(events.NewMessage(outgoing=True, pattern=r"^(جلب|ديدي جلب)\s+"))
async def fetch_restricted_content(event):
    import time
    import os
    
    raw_text = event.raw_text.strip()
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
                
            # 2. جلب الرسالة المطلوبة من السيرفر باستخدام ABH
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
            # تنظيف كافة الملفات المؤقتة فوراً
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

@ABH.on(events.NewMessage(outgoing=True))
async def didi_handler(event):
    raw_text = event.raw_text
    
    # 🔍 الفحص السيبراني التلقائي للروابط في رسائلك الشخصية (في البداية تماماً)
    security_alert = cyber_link_scanner(raw_text)
    if security_alert: 
        await event.reply(security_alert)
        return

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
                full = await ABH(GetFullChannelRequest(chat))
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
                full = await ABH(GetFullChatRequest(chat_id))
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
        report = await get_advanced_radar_stats(ABH)
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
        
        if reply_msg:
            target = reply_msg.sender_id
        else:
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
        match_ip = re.search(r'(?:افحص|فحص)\s+(?:الأيبي|الايب|ايبي|ايب)\s+([\d\.]+)', raw_text, flags=re.IGNORECASE)
        if match_ip:
            target_ip = match_ip.group(1)
            await event.reply(ip_lookup(target_ip.strip()))
        return

    if re.search(r'(?:افحص|فحص)\s+بورتات\s+([^\s]+)', raw_text, flags=re.IGNORECASE):
        match_port = re.search(r'(?:افحص|فحص)\s+بورتات\s+([^\s]+)', raw_text, flags=re.IGNORECASE)
        if match_port:
            target_host = match_port.group(1)
            status_msg = await event.reply("⚡ جاري فحص البورتات الأساسية سيبرانياً، ثواني...")
            report = await scan_ports(target_host.strip())
            await status_msg.edit(report)
        return

    if raw_text.startswith("ديدي فحص يوزر "):
        target_user = raw_text.replace("ديدي فحص يوزر ", "").strip()
        status_msg = await event.reply("🕵️‍♂️ جاري تتبع وفحص المعرف الاستخباراتي عبر المنصات العالمية...")
        report = await osint_username_lookup(target_user)
        await status_msg.edit(report, link_preview=False)
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
