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

# --- ГЛАВНЫЙ ОБРАБОТЧИК (ТВОЕ РАБОЧЕЕ РЕШЕНИЕ) ---
@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        user_id = message.chat.id
        
        # Если сессии нет — создаем её с твоей инструкцией
        if user_id not in chats:
            chats[user_id] = model.start_chat(history=[])
            # Задаем роль через системное сообщение
            instruction = (
                "Ты — дерзкий, саркастичный и язвительный близнец пользователя. "
                "Отвечай кратко и остро. Твоя задача — высмеивать глупость. "
                "Никакой вежливости, только чистый сарказм."
            )
            chats[user_id].send_message(instruction)

        # Отправляем сообщение в сессию (Gemini сам запомнит контекст)
        response = chats[user_id].send_message(message.text)
        answer = response.text
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Даже мои нейроны не выдержали этого кринжа. Попробуй еще раз.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/telegram")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
