import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# 1. Считываем данные
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("RENDER_URL")

# Настройка Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Диагностика запущена"

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
    print(f"Пришло сообщение: {message.text}") # Это увидим в логах Render
    try:
        # ШАГ 1: Проверка связи с ИИ
        bot.send_chat_action(message.chat.id, 'typing')
        
        # ШАГ 2: Запрос к Gemini
        # Мы не используем сессии пока, просто прямой запрос для теста
        response = model.generate_content(f"Ты дерзкий близнец. Ответь на это: {message.text}")
        
        # ШАГ 3: Проверка ответа
        if response and response.text:
            # Если всё ок, он пришлет ответ ИИ
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ ИИ прислал пустой ответ.")

    except Exception as e:
        # Если произойдет ЛЮБАЯ ошибка, бот напишет её тебе прямо в чат!
        error_text = f"❌ ОШИБКА: {str(e)}"
        print(error_text)
        bot.reply_to(message, error_text)

if __name__ == "__main__":
    bot.remove_webhook()
    # Очищаем очередь старых сообщений
    bot.set_webhook(url=f"{URL}/telegram", drop_pending_updates=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
