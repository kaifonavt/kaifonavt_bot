import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "mistral")

# Подключение к базе данных
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# Инициализация базы данных
def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            content TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

# Функции работы с базой данных
def get_knowledge():
    cursor.execute("SELECT title, content FROM knowledge_base")
    return cursor.fetchall()

def add_fact(title, content):
    cursor.execute("INSERT OR REPLACE INTO knowledge_base (title, content) VALUES (?, ?)", (title, content))
    conn.commit()

def delete_fact(title):
    cursor.execute("DELETE FROM knowledge_base WHERE title = ?", (title,))
    conn.commit()

def get_user_history(user_id, limit=10):
    cursor.execute('''
        SELECT role, content FROM messages
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    return list(reversed([{"role": r[0], "content": r[1]} for r in rows]))

def add_message(user_id, role, content):
    cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()

def reset_history(user_id):
    cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()

# Функция для обращения к Ollama API
def ask_ollama(prompt, model=DEFAULT_MODEL):
    # Вежливый и краткий промпт с уважением к собеседнику
    respectful_prompt = f"""
    Ты — вежливый и информированный ассистент. Ответь уважительно и кратко.
    Пользователь обратился с вопросом: "{prompt}"

    Будь кратким, точным и используй уважительные формы общения. Пример:
    - Если это вопрос о фактах, дай ответ в форме "Да, [факт]" или "Нет, [объяснение]".
    - Если это общий вопрос, постарайся дать короткий и ясный ответ, избегая лишней информации.
    """
    try:
        response = requests.post(
            f"{OLLAMA_API}/api/generate",
            json={
                "model": model,
                "prompt": respectful_prompt,
                "stream": False
            }
        )
        return response.json().get("response", "❌ Ошибка генерации")
    except Exception as e:
        return f"⚠️ Ошибка подключения к Ollama:\n{e}"
