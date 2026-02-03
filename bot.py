import os
from flask import Flask, request
import telebot
from google import genai

# 1. Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# 2. Инициализация нового клиента (Двигатель 2026)
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-1.5-flash"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "New GenAI Engine Active"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

# 3. Обработчик (Без эха, только ИИ)
@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        # Инструкция для дерзости
        instruction = "Ты — дерзкий близнец. Хами, язви, отвечай кратко."
        
        # Запрос через новый интерфейс
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"{instruction}\n\nПользователь: {message.text}"
        )
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ ИИ промолчал.")

    except Exception as e:
        # Если будет ошибка, мы увидим её точную причину
        bot.reply_to(message, f"❌ Ошибка нового API: {str(e)[:100]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # Чистим очередь, чтобы старые фразы не повторялись
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
