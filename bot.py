import os
import telebot
from groq import Groq

# Получаем ключи из переменных окружения
TOKEN = os.getenv("8283418346:AAEAjnXRqdhyetKeGBuinjocz9SfUKfNt_s")
GROQ_API_KEY = os.getenv("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")

# Инициализация бота и Groq-клиента
bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    try:
        # Отправляем текст в Groq
        chat = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Ты дерзкий и саркастичный близнец. Хами."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.9
        )

        # Отвечаем пользователю
        bot.reply_to(message, chat.choices[0].message.content)

    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

if __name__ == "__main__":
    print("Бот запущен")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending_updates=True)
