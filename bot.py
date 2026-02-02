import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# 1. Считываем данные
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# 2. НАСТРОЙКА ИИ (ИСПРАВЛЕНА ВЕРСИЯ API)
# Мы явно указываем версию v1, чтобы убрать ошибку 404
genai.configure(api_key=API_KEY, transport='rest') 

# Используем максимально стабильное имя модели
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище чатов
chats = {}

@app.route("/")
def home():
    return "Fix 404 Active"

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
        # Если чата нет — создаем
        if user_id not in chats:
            # Начинаем чат (без истории v1beta)
            chats[user_id] = model.start_chat(history=[])
            # Первое сообщение-настройка (скрыто)
            chats[user_id].send_message("Ты — дерзкий близнец. Хами.")

        # Отправляем сообщение
        response = chats[user_id].send_message(message.text)
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ Пустой ответ от ИИ.")

    except Exception as e:
        # Выводим подробную ошибку в чат
        error_msg = str(e)
        bot.reply_to(message, f"❌ Ошибка: {error_msg[:150]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # Очищаем "застрявшие" сообщения
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
