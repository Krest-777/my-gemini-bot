import os
from flask import Flask, request
import telebot
from google import genai # Используем новую библиотеку

# Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# Инициализация нового клиента Gemini
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-1.5-flash"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище контекста (простая версия для проверки)
chats_context = {}

@app.route("/")
def home():
    return "Gemini 2026 Engine Active"

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
        # Инструкция для дерзости
        instruction = "Ты — дерзкий близнец. Хами, язви, отвечай коротко."
        full_prompt = f"{instruction}\n\nПользователь: {message.text}\nБлизнец:"

        # Запрос через НОВЫЙ метод (обходит ошибку 404)
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=full_prompt
        )
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ ИИ промолчал.")

    except Exception as e:
        # Выводим конкретную ошибку
        bot.reply_to(message, f"❌ Ошибка нового API: {str(e)[:150]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # Чистим очередь, чтобы не было повторов старых фраз
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
