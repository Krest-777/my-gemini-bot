import os
from flask import Flask, request
import telebot
from google import genai # Используем новый пакет, как просит Render

# 1. Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# 2. Инициализация нового клиента Gemini
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-1.5-flash"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Новый движок 2026 активен"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

# 3. Единственный обработчик (БЕЗ ЭХО-ПОВТОРА)
@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        # Инструкция для твоего дерзкого близнеца
        instruction = "Ты — дерзкий, саркастичный близнец пользователя. Отвечай кратко и язвительно."
        
        # Запрос к ИИ через новый метод
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"{instruction}\n\nПользователь: {message.text}"
        )
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ ИИ промолчал. Проверь ключи.")

    except Exception as e:
        # Выводим ошибку прямо в чат, чтобы сразу видеть причину
        bot.reply_to(message, f"❌ Ошибка API: {str(e)[:150]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # Сброс очереди уберет эффект "попугая" для старых сообщений
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
