import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== KONFIGURASI =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
BLUESMINDS_API_KEY = os.environ.get("BLUESMINDS_API_KEY")
BLUESMINDS_URL = "https://api.bluesminds.com/v1/chat/completions"

# ===== LOGGING =====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== FUNGSI PANGGIL AI =====
async def get_ai_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {BLUESMINDS_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    try:
        response = requests.post(BLUESMINDS_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return "Maaf, terjadi kesalahan."

# ===== HANDLER =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim pesan apa saja, saya akan balas dengan AI.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message:
        return
    await update.message.chat.send_action(action="typing")
    ai_reply = await get_ai_response(user_message)
    await update.message.reply_text(ai_reply[:4096])

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Error: {context.error}")

# ===== MAIN =====
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("Bot berjalan...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
