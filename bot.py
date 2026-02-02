import os
from flask import Flask, request
import telebot
import google.generativeai as genai
from collections import defaultdict

# --- КОНФИГУРАЦИЯ ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

genai.configure(api_key=GEMINI_API_KEY)

# Настройка модели с твоим "хаосом"
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1.2,
        "top_p": 0.95,
    }
)

# Хранилище чат-сессий для каждого пользователя
chats = {}

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Близнец 3.0: Сессии + Промпт + Хаос активен!"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403
# --- ОТСЮДА И ДО КОНЦА ФАЙЛА ЗАМЕНИ ВСЁ ---

# Хранилище чат-сессий
chats = {}

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Близнец во Франкфурте активен!"

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
    try:
        user_id = message.chat.id
        
        # Если сессии нет — создаем её
        if user_id not in chats:
            chats[user_id] = model.start_chat(history=[])
            # Первая команда боту (скрытая от пользователя)
            chats[user_id].send_message("Ты — мой дерзкий близнец. Твоя задача: хамить, язвить и отвечать коротко. Понял?")

        # Отправляем сообщение пользователя в Gemini
        response = chats[user_id].send_message(message.text)
        
        # Отвечаем пользователю текстом от ИИ
        bot.reply_to(message, response.text)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "У меня нейроны заплелись от твоей тупости.")

if name == "__main__":
    bot.remove_webhook()
    # Убедись, что в Render переменная RENDER_URL без слэша в конце!
    bot.set_webhook(url=f"{RENDER_URL}/telegram")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
