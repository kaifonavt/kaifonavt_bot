import os
import telebot
from dotenv import load_dotenv
from core import generate_response

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

@bot.message_handler(commands=['start', 'help'])
def help_command(message):
    help_text = (
        "Привет! Я ИИ-бот, отвечаю на основе базы знаний.\n\n"
        "Команды:\n"
        "/help — Показать справку\n"
        "/reset — Сбросить историю диалога\n"
        "Задай мне любой вопрос!"
    )
    bot.reply_to(message, help_text)


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    response = generate_response(message.from_user.id, message.text)
    bot.reply_to(message, response)

bot.polling()
