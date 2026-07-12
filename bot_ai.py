import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== KONFIGURASI =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = "https://capi.aerolink.lat/"

# ===== LOGGING =====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== FUNGSI PANGGIL AI =====
async def get_ai_response(prompt: str) -> str:
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        # 🔥 PERBAIKAN: Gunakan ANTHROPIC_BASE_URL langsung
        response = requests.post(
            f"{ANTHROPIC_BASE_URL}/v1/messages",  # <- endpoint lengkap
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return "Maaf, terjadi kesalahan."

# ===== HANDLER =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim pesan apa saja, saya akan balas dengan AI Claude.")

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
    print("Bot berjalan dengan Claude via Aerolink...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
