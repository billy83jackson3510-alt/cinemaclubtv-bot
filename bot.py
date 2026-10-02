import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

VIDEOS = {
    "film": {
        "title": "دانلود فیلم و سریال",
        "qualities": {
            "1080": "BAACAgQAAxkBAAIsQGq_jcsey_KQYjGAb3GcDwZ_qAq-AAJ6IQACP6P5USksUuqvJAiiPQQ",
            "720": "BAACAgQAAxkBAAIsPmq_jb-1ncrD0YwqzNIk_yZc0vQSAAJ5IQACP6P5UcBW6660toyOPQQ",
            "480": "BAACAgQAAxkBAAIsK2q_jKXqpaISmjLp65pZKCNERhV9AAJ2IQACP6P5UeKktomi7gflPQQ",
        }
    }
}

logging.basicConfig(level=logging.INFO)

async def delete_messages(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    message_ids = job.data["message_ids"]

    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except:
            pass

    keyboard = [[InlineKeyboardButton("🔄 دانلود مجدد", callback_data=f"redownload_{job.data['video_key']}")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="⏰ زمان ۲ دقیقه‌ای تموم شد و ویدیوها پاک شدن.\n\nاگر هنوز نیاز داری، دوباره دانلود کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_videos(chat_id: int, context: ContextTypes.DEFAULT_TYPE, video_key: str):
    if video_key not in VIDEOS:
        await context.bot.send_message(chat_id=chat_id, text="این محتوا پیدا نشد.")
        return

    video_data = VIDEOS[video_key]

    warning = await context.bot.send_message(
        chat_id=chat_id,
        text="⚠️ <b>فقط ۲ دقیقه وقت داری ویدیوها رو سیو کنی!</b>\nبعد از ۲ دقیقه همه پیام‌ها پاک می‌شن.",
        parse_mode="HTML"
    )

    message_ids = [warning.message_id]

    for quality, file_id in video_data["qualities"].items():
        msg = await context.bot.send_video(
            chat_id=chat_id,
            video=file_id,
            caption=f"🎬 {video_data['title']}\nکیفیت: {quality}p",
            supports_streaming=True
        )
        message_ids.append(msg.message_id)

    context.job_queue.run_once(
        delete_messages,
        when=120,
        data={
            "chat_id": chat_id,
            "message_ids": message_ids,
            "video_key": video_key
        },
        name=f"delete_{chat_id}_{video_key}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("لطفاً از طریق کانال اصلی وارد شوید.")
        return

    video_key = args[0]
    await send_videos(update.effective_chat.id, context, video_key)

async def redownload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    video_key = query.data.replace("redownload_", "")
    await send_videos(query.message.chat_id, context, video_key)

def main():
    if not TOKEN:
        print("خطا: BOT_TOKEN تنظیم نشده!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(redownload, pattern="^redownload_"))
    print("ربات با موفقیت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
