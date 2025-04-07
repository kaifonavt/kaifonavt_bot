import telebot
import requests
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "mistral")

bot = telebot.TeleBot(BOT_TOKEN)
user_model = {}

def ask_ollama(prompt, model=DEFAULT_MODEL):
    try:
        response = requests.post(
            f"{OLLAMA_API}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "❌ Ошибка генерации")
    except Exception as e:
        return f"⚠️ Ошибка подключения к Ollama:\n{e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Привет! Я локальный AI-бот на базе Ollama 😎\n"
                     "Отправь мне сообщение — и я отвечу.\n"
                     "Используй /model чтобы выбрать модель.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     "ℹ️ Помощь:\n"
                     "- Напиши любое сообщение — я отвечу\n"
                     "- /model — выбрать модель\n"
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    model = user_model.get(message.from_user.id, DEFAULT_MODEL)
    bot.send_chat_action(message.chat.id, 'typing')
    response = ask_ollama(message.text, model=model)
    bot.reply_to(message, response)

print("🤖 Бот запущен.")
bot.polling()
