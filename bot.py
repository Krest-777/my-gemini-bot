import os
from flask import Flask, request
import telebot
from google import genai

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

client = genai.Client(api_key=API_KEY)
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home(): return "OK"

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
        # ПРОВЕРКА: Если бот повторит это, значит ИИ живой
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Ты дерзкий близнец. Ответь на: {message.text}"
        )
        # Бот ОТВЕЧАЕТ текстом от ИИ + добавляет метку версии
        bot.reply_to(message, f"[V2 Active]: {response.text}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)[:50]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # drop_pending_updates=True — это КЛЮЧ к успеху
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
