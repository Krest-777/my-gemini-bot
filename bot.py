import telebot
import google.generativeai as genai
import os
from flask import Flask
import threading

# =========================
# КЛЮЧИ (ЗАМЕНИ ПОТОМ)
# =========================
GOOGLE_API_KEY = "AIzaSyCJqyEL3Mm2XWyzsxQLkGIyUFPS1ezO2Vw"
TELEGRAM_TOKEN = "7970873259:AAHYoDCgeyCHq1KKB6DvDAK7cpX4ikjqukM"

# =========================
# НАСТРОЙКА GEMINI
# =========================
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=(
        "Ты — дерзкий и острый на язык близнец пользователя. "
        "Отвечай кратко, с сарказмом. "
        "Ты не любишь видео и медиа."
    )
)

# =========================
# TELEGRAM + FLASK
# =========================
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Близнец в сети!"

# =========================
# ОБРАБОТКА ВИДЕО
# =========================
@bot.message_handler(content_types=['video', 'video_note'])
def handle_video(message):
    bot.reply_to(
        message,
        "Ты че мне видео суешь? Я че, по-твоему, телек? Пиши текстом, не беси меня!"
    )

# =========================
# ОБРАБОТКА ТЕКСТА
# =========================
@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(
            message,
            "Даже я сломался от твоих сообщений."
        )

# =========================
# ЗАПУСК
# =========================
if name == "__main__":
    # Запускаем Telegram-бота в отдельном потоке
    threading.Thread(
        target=lambda: bot.infinity_polling(skip_pending=True),
        daemon=True
    ).start()

    # Flask нужен для хостинга (Render / Railway и т.п.)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
