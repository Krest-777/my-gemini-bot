import os
import telebot
from google import genai

# Только два ключа. Больше ничего не нужно!
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

# Инициализация ИИ
client = genai.Client(api_key=API_KEY)
bot = telebot.TeleBot(TOKEN)

print("Бот запущен в режиме Polling...")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        # Прямой запрос к Gemini
        prompt = f"Ты мой дерзкий близнец. Хами и язви. Ответь коротко: {message.text}"
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # Отправляем только то, что придумал ИИ
        if response.text:
            bot.send_message(message.chat.id, response.text)
        else:
            bot.send_message(message.chat.id, "Даже у меня нет слов на твой бред.")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка API: {str(e)[:50]}")

# Запуск бесконечного опроса (убивает старые вебхуки автоматически)
if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling(skip_pending_updates=True)
