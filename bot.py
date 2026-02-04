import os
import telebot
from google import genai

# Берем только два ключа. RENDER_URL больше НЕ НУЖЕН.
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

# Инициализация
client = genai.Client(api_key=API_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    try:
        # Прямой запрос к ИИ
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Ты — мой дерзкий и саркастичный близнец. Хами. Ответь на: {message.text}"
        )
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "Я промолчу, это слишком тупо.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)[:50]}")

if __name__ == "__main__":
    print("Бот запущен в режиме Long Polling...")
    # Убиваем старые вебхуки, чтобы они не мешали
    bot.remove_webhook()
    # Запускаем бесконечный опрос
    bot.infinity_polling(skip_pending_updates=True)
