import os
import telebot
from dotenv import load_dotenv
from telebot import types
from core import generate_response, save_message

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

@bot.message_handler(commands=['start'])
def welcome_message(message):
    user_first_name = message.from_user.first_name
    welcome_text = (
        f"Привет, {user_first_name}! Я ИИ-бот, созданный для помощи с ответами на любые вопросы.\n"
        "Напиши /help для инструкции или /info, чтобы узнать больше."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🧠 Я ИИ-бот, обученный на базе знаний.\n\n"
        "Ты можешь:\n"
        "• Задавать любые вопросы — я постараюсь ответить.\n"
        "• Команды:\n"
        "  /start — перезапустить диалог\n"
        "  /help — справка\n"
        "  /info — полезные ссылки"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['info'])
def info_command(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Связаться с создателем", url="https://t.me/kaifonavt"),
        types.InlineKeyboardButton("Перейти на сайт 1", url="https://www.site1.com"),
        types.InlineKeyboardButton("Перейти на сайт 2", url="https://www.site2.com")
    )
    bot.send_message(message.chat.id, "🔗 Полезные ссылки:", reply_markup=markup)

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def handle_message(message):
    user_id = str(message.from_user.id)
    user_text = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = generate_response(user_id, user_text)
        bot.reply_to(message, response)
    except Exception as e:
        error_text = f"⚠️ Произошла ошибка: {e}"
        bot.reply_to(message, error_text)

print("🤖 Бот запущен...")
bot.polling(none_stop=True)
