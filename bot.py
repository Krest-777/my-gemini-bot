import os
from flask import Flask, request
import telebot
import google.generativeai as genai
from collections import defaultdict, deque

# ====================================
# CONFIG
# ====================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

genai.configure(api_key=GEMINI_API_KEY)

# ПАМЯТЬ: Храним последние 6 сообщений для каждого пользователя
chat_memory = defaultdict(lambda: deque(maxlen=6))

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="Ты – токсичный, саркастичный близнец. Отвечай резко, но остроумно. Не будь вежливым."
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Близнец во Франкфурте в сети!"

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    return "error", 403

# ====================================
# ОБРАБОТКА ТЕКСТА (С ПАМЯТЬЮ)
# ====================================
@bot.message_handler(content_types=['text'])
def chat(message):
    try:
        user_id = message.chat.id
        
        # Добавляем сообщение пользователя в память
        chat_memory[user_id].append(f"Пользователь: {message.text}")
        
        # Собираем контекст из памяти
        context = "\n".join(chat_memory[user_id])
        
        # Генерируем ответ на основе контекста
        response = model.generate_content(context)
        answer = response.text
        
        # Добавляем ответ бота в память
        chat_memory[user_id].append(f"Близнец: {answer}")
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        bot.reply_to(message, "Я завис. Ты слишком скучный для моих процессоров.")

# ====================================
# STARTUP
# ====================================
if name == "__main__":
    bot.remove_webhook()
    # Убедись, что в Render URL указан верно (без / в конце)
    bot.set_webhook(url=f"{RENDER_URL}/telegram")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
