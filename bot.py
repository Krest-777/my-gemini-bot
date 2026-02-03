import os
from flask import Flask, request
import telebot
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# 1. Настройки из Render
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# 2. Настройка ИИ (Лечим ошибку 404)
genai.configure(api_key=API_KEY)

# Принудительно задаем модель через стабильную версию v1
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Память чатов
chats = {}

@app.route("/")
def home():
    return "Status: Fixed & Online"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

# 3. Единственный обработчик (УБРАНО ЭХО)
@bot.message_handler(content_types=['text'])
def chat(message):
    user_id = message.chat.id
    try:
        # Если сессии нет — создаем с ПРАВИЛЬНОЙ настройкой
        if user_id not in chats:
            chats[user_id] = model.start_chat(history=[])
            # Инструкция (отправляем через стабильный запрос)
            chats[user_id].send_message(
                "Ты — дерзкий близнец. Хами и язви.",
                request_options=RequestOptions(api_version='v1')
            )

        # Отправляем сообщение пользователя
        response = chats[user_id].send_message(
            message.text,
            request_options=RequestOptions(api_version='v1')
        )
        
        # Шлем только ответ ИИ
        bot.reply_to(message, response.text)
        
    except Exception as e:
        error_msg = str(e)
        # Если все еще 404, мы это увидим
        bot.reply_to(message, f"❌ Ошибка API: {error_msg[:100]}")

if __name__ == "__main__":
    bot.remove_webhook()
    # Очистка очереди (drop_pending_updates) уберет повторы старых фраз
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
