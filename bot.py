import os
from flask import Flask, request
import telebot
import google.generativeai as genai
from collections import defaultdict

# 1. ПОЛУЧАЕМ КЛЮЧИ (Они должны быть в Environment Variables на Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# 2. НАСТРОЙКА ГЕМИНИ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1.2, # Чтобы он был дерзким
        "top_p": 0.95,
    }
)

# Хранилище чатов в памяти сервера
chats = {}

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Близнец во Франкфурте онлайн!"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

# 3. ЕДИНСТВЕННЫЙ ОБРАБОТЧИК (Никаких повторов!)
@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        user_id = message.chat.id
        
        # Если чат еще не создан — создаем его с инструкцией
        if user_id not in chats:
            chats[user_id] = model.start_chat(history=[])
            # Первая команда боту
            chats[user_id].send_message("Ты — мой дерзкий близнец. Хами и язви. Отвечай коротко.")

        # Получаем ответ от нейронки (Gemini)
        response = chats[user_id].send_message(message.text)
        
        # ВАЖНО: Мы отправляем ответ ИИ, а не текст пользователя
        bot.reply_to(message, response.text)
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        # Если ИИ не ответил, мы шлем это, чтобы понять, что была ошибка
        bot.reply_to(message, "Даже мои нейроны в шоке. Попробуй еще раз.")

if __name__ == "__main__":
    bot.remove_webhook()
    # Убедись, что RENDER_URL в настройках правильный!
    bot.set_webhook(url=f"{RENDER_URL}/telegram")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
