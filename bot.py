import os
import time
from flask import Flask, request
import telebot
import google.generativeai as genai

# Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return f"Server time: {time.ctime()}"

@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        # Диагностическая метка: мы сразу увидим, новый это код или старый
        print(f"DEBUG: Обработка сообщения {message.text}")
        
        # Прямой запрос к ИИ
        response = model.generate_content(f"Ответь дерзко: {message.text}")
        
        if response and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ ИИ выдал пустой ответ (чекни ключи).")
            
    except Exception as e:
        # Если снова 404, бот напишет это ПРЯМО СЕЙЧАС
        bot.reply_to(message, f"❌ ОШИБКА: {str(e)[:100]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # Чистим очередь сообщений!
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
