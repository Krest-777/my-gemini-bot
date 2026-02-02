import telebot
import google.generativeai as genai
import os
from flask import Flask
import threading

# ТВОИ КЛЮЧИ (Оставил те, что были на скринах)
GOOGLE_API_KEY = "AIzaSyDtMBt8smr9avUUzvS1WjxzwqvW4pz2Pic"
TELEGRAM_TOKEN = "7970873259:AAEc5BB2gb5n8Cwxr8uxVXotftMAUGt3uQs"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Мини-сервер для стабильной работы на Render
app = Flask(__name__)
@app.route('/')
def home(): return "Бот запущен и работает!"

@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if name == "__main__":
    # Запуск бота
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    # Запуск веб-сервера на порту Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
