import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# === ENV ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# === GEMINI ===
genai.configure(api_key=API_KEY)

# СТАБИЛЬНАЯ модель
model = genai.GenerativeModel("gemini-pro")

# === TELEGRAM + FLASK ===
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Память чатов
chats = {}

@app.route("/")
def home():
    return "Status: Online"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

# === ЕДИНСТВЕННЫЙ HANDLER ===
@bot.message_handler(content_types=["text"])
def chat(message):
    user_id = message.chat.id

    try:
        if user_id not in chats:
            chats[user_id] = model.start_chat(history=[])
            chats[user_id].send_message(
                "Ты — дерзкий близнец. Хами и язви."
            )

        response = chats[user_id].send_message(message.text)

        bot.reply_to(message, response.text)

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка ИИ: {str(e)[:120]}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"{URL}/telegram",
        drop_pending_updates=True
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
