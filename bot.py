import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TOKEN = "8264972630:AAHtB3idvs43-gYvDMIwCyBOOmvRs8kxnZ4"
CHANNEL_USERNAME = "@PessSTORE7"
OWNER_ID = 6891544595

users = set()

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users.add(user.id)

    await update.message.reply_text(
        "👋 مرحباً بك في بوت تحميل انستقرام وتيك توك\n\n"
        "📌 ارسل الرابط وسيتم التحميل مباشرة.\n\n"
        "⚠️ يجب الاشتراك في القناة أولاً."
    )

# ================= CHECK SUB =================
async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= DOWNLOAD =================
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.effective_user.id

    if not await check_subscription(user_id, context.bot):
        await update.message.reply_text(
            "⚠️ اشترك أولاً في القناة:\nhttps://t.me/PessSTORE7"
        )
        return

    url = update.message.text.strip()

    if "instagram.com" not in url and "tiktok.com" not in url:
        await update.message.reply_text("ارسل رابط انستقرام او تيك توك فقط")
        return

    await update.message.reply_text("⏳ جاري التحميل...")

    ydl_opts = {
    "format": "mp4",
    "outtmpl": "video.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, "rb") as video_file:
            await update.message.reply_video(video=video_file)

        os.remove(filename)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ حدث خطأ في التحميل")

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    message = " ".join(context.args)

    for user_id in users:
        try:
            await context.bot.send_message(user_id, message)
        except:
            pass

    await update.message.reply_text("✅ تم الإرسال للجميع")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

app.run_polling()
