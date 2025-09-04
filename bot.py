import os
import asyncio
from google import genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- 1) Секреты из переменных окружения ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Не найден TELEGRAM_BOT_TOKEN")
if not GEMINI_API_KEY:
    raise RuntimeError("Не найден GEMINI_API_KEY")

# --- 2) Клиент Gemini (официальный SDK) ---
# Документация и квикстарт: google-genai, модель gemini-2.5-flash
# https://ai.google.dev/gemini-api/docs/quickstart
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# --- 3) Приветствие на /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот на Google Gemini. Напишите мне что-нибудь!"
    )

# --- 4) Ответы на любые текстовые сообщения ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text or ""
    try:
        # Вызов SDK синхронный → уносим в отдельный поток, чтобы не блокировать event loop PTB
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=user_text,
        )
        reply = response.text or "Извините, ответа нет."
    except Exception as e:
        reply = f"⚠️ Ошибка: {e}"

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()  # long polling

if __name__ == "__main__":
    main()
