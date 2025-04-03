import telebot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я простой бот. Напиши что-нибудь, и я повторю твое сообщение.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

print("Бот запущен...")
bot.infinity_polling()
