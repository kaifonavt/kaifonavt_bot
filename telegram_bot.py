import telebot
from telebot import types
from llm_core import (
    init_db,
    add_fact,
    delete_fact,
    get_knowledge,
    reset_history,
    ask_ollama,
    add_message,
    get_user_history
)
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
user_model = {}

# Инициализация базы данных
init_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Привет! Я локальный AI-бот на базе Ollama 😎\n"
                     "Отправь мне сообщение — и я отвечу.\n"
                     "Используй /model чтобы выбрать модель.\n"
                     "Для добавления или удаления фактов используй /addfact и /delfact.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     "ℹ️ Помощь:\n"
                     "- Напиши любое сообщение — я отвечу\n"
                     "- /model — выбрать модель\n"
                     "- /addfact — добавить факт в базу знаний\n"
                     "- /delfact — удалить факт из базы знаний\n"
                     "- Все работает локально через Ollama")

@bot.message_handler(commands=['model'])
def choose_model(message):
    markup = types.InlineKeyboardMarkup()
    for model in ["mistral", "llama2", "codellama", "gemma", "phi"]:
        markup.add(types.InlineKeyboardButton(model, callback_data=f"model_{model}"))
    bot.send_message(message.chat.id, "Выбери модель:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("model_"))
def callback_model(call):
    model = call.data.split("_")[1]
    user_model[call.from_user.id] = model
    bot.answer_callback_query(call.id, f"Модель выбрана: {model}")
    bot.send_message(call.message.chat.id, f"✅ Теперь используется модель: *{model}*", parse_mode="Markdown")

@bot.message_handler(commands=['addfact'])
def handle_addfact(message):
    try:
        parts = message.text[len("/addfact "):].split("|", 1)
        title, content = parts[0].strip(), parts[1].strip()
        add_fact(title, content)
        bot.reply_to(message, f"Факт '{title}' добавлен.")
    except:
        bot.reply_to(message, "Формат: /addfact title | content")

@bot.message_handler(commands=['delfact'])
def handle_delfact(message):
    title = message.text[len("/delfact "):].strip()
    delete_fact(title)
    bot.reply_to(message, f"Факт '{title}' удалён.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    model = user_model.get(message.from_user.id, "mistral")
    
    # Получаем все факты из базы данных
    facts = get_knowledge()
    kb_text = "\n".join([f"{title}: {content}" for title, content in facts])

    # Добавляем факты в запрос
    prompt = f"Ты бот, использующий базу знаний. Ответь на основе этих фактов:\n{kb_text}\n\nПользователь: {message.text}"

    bot.send_chat_action(message.chat.id, 'typing')
    response = ask_ollama(prompt, model=model)
    bot.reply_to(message, response)

# Запуск бота
print("🤖 Бот запущен.")
bot.polling()
