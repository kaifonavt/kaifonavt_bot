import os
import telebot
from dotenv import load_dotenv
from telebot import types
from core import generate_response

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

@bot.message_handler(commands=['start'])
def welcome_message(message):
    user_first_name = message.from_user.first_name
    welcome_text = (
        f"Привет, {user_first_name}! Я ИИ-бот, созданный для того, чтобы помогать тебе с ответами на вопросы.\n"
        "Если ты хочешь узнать, как я работаю, напиши /help.\n"
        "Если хочешь связаться с создателем или посетить сайты, используй команду /info."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "Привет! Я ИИ-бот, отвечаю на основе базы знаний.\n\n"
        "Команды:\n"
        "Задай мне любой вопрос!"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['info'])
def info_command(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_telegram = types.InlineKeyboardButton("Связаться с создателем", url="https://t.me/kaifonavt")
    btn_site1 = types.InlineKeyboardButton("Перейти на сайт 1", url="https://www.site1.com")
    btn_site2 = types.InlineKeyboardButton("Перейти на сайт 2", url="https://www.site2.com")
    markup.add(btn_telegram, btn_site1, btn_site2)
    bot.send_message(message.chat.id, "Вот несколько ссылок для вас:", reply_markup=markup)

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def handle_message(message):
    user_id = message.from_user.id
    response = generate_response(user_id, message.text)
    bot.reply_to(message, response)

bot.polling()
