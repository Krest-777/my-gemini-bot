import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# Настройка ИИ - ИСПРАВЛЕНО НАЗВАНИЕ МОДЕЛИ
genai.configure(api_key=API_KEY)
# Используем 'gemini-1.5-flash-latest' для обхода ошибки 404
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Память сессий
chats = {}

@app.route("/")
def home():
    return "Diagnostic Fix Active"

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
        # Инициализация чата, если его нет
        if user_id not in chats:
            chats[user_id] = model.start_chat(history=[])
            # Первая системная команда
            chats[user_id].send_message("Ты — дерзкий близнец. Хами и язви.")

        # Пытаемся получить ответ
        response = chats[user_id].send_message(message.text)
        
        if response and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ Модель ответила пустотой. Попробуй другое слово.")

    except Exception as e:
        # Выводим ошибку, чтобы видеть, если 404 сменится на что-то другое
        bot.reply_to(message, f"❌ Ошибка связи с ИИ: {str(e)[:100]}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
