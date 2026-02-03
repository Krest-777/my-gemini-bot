import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# Настройка Gemini
genai.configure(api_key=API_KEY)

# Мы убираем лишние приставки, оставляем только суть
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

chats = {}

@app.route("/")
def home():
    return "System Rebooted"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

@bot.message_handler(content_types=['text'])
def chat(message):
    user_id = message.chat.id
    try:
        # Прямой запрос без наворотов для проверки
        # Если это сработает, значит API ожило
        prompt = f"Ты — дерзкий близнец. Ответь коротко: {message.text}"
        response = model.generate_content(prompt)
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ Пусто.")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)[:100]}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
