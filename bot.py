import telebot
import google.generativeai as genai
import os
from flask import Flask
import threading

# ТВОИ КЛЮЧИ
GOOGLE_API_KEY = "AIzaSyDtMBt8smr9avUUzvS1WjxzwqvW4pz2Pic"
TELEGRAM_TOKEN = "7970873259:AAEc5BB2gb5n8Cwxr8uxVXotftMAUGt3uQs"

genai.configure(api_key=GOOGLE_API_KEY)
# Настройка характера: дерзкий близнец
model = genai.GenerativeModel('gemini-1.5-flash', 
    system_instruction="Ты — дерзкий и острый на язык близнец пользователя. Отвечай кратко, с сарказмом и подколами. Ты не любишь видео и тупые вопросы.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): return "Близнец в сети и готов язвить!"

# РЕАКЦИЯ НА ВИДЕО И КРУЖОЧКИ
@bot.message_handler(content_types=['video', 'video_note'])
def handle_video(message):
    bot.reply_to(message, "Ты че мне видео суешь? Я че, по-твоему, телек? Пиши текстом, если есть че сказать, не беси меня!")

# ОБЫЧНЫЕ СООБЩЕНИЯ
@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Даже я сломался от твоих сообщений. Попробуй еще раз.")

if name == "__main__":
    # Исправленная строка запуска
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
