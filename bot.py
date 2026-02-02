import os
from flask import Flask, request
import telebot
import google.generativeai as genai
from collections import defaultdict, deque

# Конфигурация из Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# Настройка ИИ с "эффектом хаоса"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1.2,  # Высокая креативность и дерзость
        "top_p": 0.95,
    }
)

# Память (храним последние 6 реплик для контекста)
chat_memory = defaultdict(lambda: deque(maxlen=6))

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Близнец 2.0 (Франкфурт + Хаос) в сети!"

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
        user_id = message.chat.id
        
        # 1. Формируем контекст из старой памяти
        context = "\n".join(chat_memory[user_id])
        
        # 2. ПРАВИЛЬНАЯ ЛОГИКА: Явный prompt без дублирования
        prompt = f"""
Ты — дерзкий, язвительный и высокомерный близнец пользователя. 
Твоя задача: отвечать максимально остроумно и токсично. 
Не повторяй свои старые шутки.

История диалога для контекста:
{context}

Новое сообщение от этого кожаного мешка: {message.text}
Твой ответ:
"""
        
        # 3. Генерация ответа
        response = model.generate_content(prompt)
        answer = response.text
        
        # 4. СОХРАНЯЕМ В ПАМЯТЬ ТОЛЬКО СЕЙЧАС (чтобы избежать зацикливания)
        chat_memory[user_id].append(f"Пользователь: {message.text}")
        chat_memory[user_id].append(f"Близнец: {answer}")
        
        bot.reply_to(message, answer)
        
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        bot.reply_to(message, "Твой вопрос настолько тупой, что у меня закоротило память. Попробуй еще раз.")

if name == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/telegram")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
