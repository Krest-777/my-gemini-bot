import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# ====================================
# CONFIG (Данные берутся из настроек Render)
# ====================================
# Забираем секретные ключи из настроек Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1.2,
        "top_p": 0.95,
    },
    system_instruction=(
        "Ты – токсичный, саркастичный близнец. "
        "Отвечай резко, но остроумно. "
        "Не будь вежливым."
    )
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# ====================================
# ROUTES
# ====================================
@app.route("/")
def home():
    return "Близнец в сети"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    else:
        return "error", 403

# ====================================
# HANDLERS
# ====================================
@bot.message_handler(content_types=["video", "video_note"])
def handle_video(message):
    bot.reply_to(
        message,
        "Ты мне видео суёшь? Я текст читаю. Пиши словами."
    )

@bot.message_handler(content_types=["text"])
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception:
        bot.reply_to(
            message,
            "Даже я сломался от твоего сообщения."
        )

# ====================================
# STARTUP
# ====================================
if __name__ == "__main__":
    # ЖЁСТКО сбрасываем всё старое
    bot.remove_webhook()
    
    # Ставим новый webhook
    # Важно: URL должен заканчиваться на /telegram
    bot.set_webhook(url=f"{RENDER_URL}/telegram")
    
    # Запускаем сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
