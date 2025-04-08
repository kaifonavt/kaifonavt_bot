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
def ask_ollama(prompt, user_id, model=DEFAULT_MODEL):
    # Получаем последние 10 сообщений пользователя для контекста
    user_history = get_user_history(user_id)

    # Извлекаем ключевые темы из текущего запроса и предыдущих сообщений
    current_query_keywords = set(prompt.lower().split())

    # Собираем только те факты, которые могут быть актуальны для текущего вопроса
    relevant_facts = []
    facts = get_knowledge()

    # Ищем факты, которые связаны с текущими ключевыми словами
    for title, content in facts:
        if any(keyword in content.lower() for keyword in current_query_keywords):
            relevant_facts.append(f"{title}: {content}")

    # Если факты найдены, включаем их в запрос
    kb_text = "\n".join(relevant_facts) if relevant_facts else ""

    respectful_prompt = f"""
    Ты — вежливый и информированный ассистент, собеседник. Ответь уважительно и кратко.
    Ответь в мужском роде. НЕ ГОВОРИТЬ НА ЧТО ТЫ ОПИРАЕШЬСЯ.
    Отвечай на языке который использовался в вопросе.
    Нельзя говорить, что ты бот или искусственный интеллект.
    Вопрос пользователя: "{prompt}"
    Используй только актуальные факты для ответа: {kb_text}
    """

    # Добавляем знания, если они есть
    if kb_text:
        respectful_prompt += f"\nИспользуй только актуальные факты для ответа: {kb_text}"

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

