import telebot
import google.generativeai as genai
import os
from flask import Flask
import threading

GOOGLE_API_KEY = "AIzaSyDtMBt8smr9avUUzvS1WjxzwqvW4pz2Pic"
TELEGRAM_TOKEN = "7970873259:AAEc5BB2gb5n8Cwxr8uxVXotftMAUGt3uQs"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if name == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
