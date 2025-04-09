import os
import telebot
from dotenv import load_dotenv
from ai_core import load_kb_from_db, query_knowledge, reset_history, vector_search

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

load_kb_from_db()

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

@bot.message_handler(commands=['reset'])
def reset_command(message):
    reset_history(message.from_user.id)
    bot.reply_to(message, "История диалога сброшена.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    response = query_knowledge(message.text, user_id=message.from_user.id)
    bot.reply_to(message, response)

@bot.message_handler(commands=['search'])
def search_command(message):
    query = message.text[len('/search '):]
    if query:
        results = vector_search(query)
        response = "\n".join([f"{fact[1]} - Similarity: {fact[2]:.4f}" for fact in results])
        bot.reply_to(message, response)

bot.polling()
