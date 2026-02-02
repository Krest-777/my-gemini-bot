import telebot
import google.generativeai as genai
import requests

# ВСТАВЬ СВОИ ДАННЫЕ СЮДА
TOKEN = '8283418346:AAEAjnXRqdhyetKeGBuinjocz9SfUKfNt_s'
GEMINI_KEY = 'AIzaSyCJqyEL3Mm2XWyzsxQLkGIyUFPS1ezO2Vw'

# Настройка Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# Настройка бота
bot = telebot.TeleBot(TOKEN)

# Принудительный сброс старых соединений
requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=True")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Температура 1.3 для дерзости
        response = model.generate_content(
            message.text,
            generation_config=genai.types.GenerationConfig(temperature=1.3)
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Я в глубоком раздумье... Попробуй еще раз!")

if name == '__main__':
    print("Новый бот вышел на охоту...")
    bot.infinity_polling(skip_pending=True)
