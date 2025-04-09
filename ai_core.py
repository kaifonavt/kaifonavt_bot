import os
import sqlite3
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import requests

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
DB_PATH = os.getenv("DB_PATH", "knowledge.db")

user_histories = {}
knowledge_base = []
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Модель для эмбеддингов (размерность 384)

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# Загружаем базу знаний и эмбеддинги для всех фактов
def load_kb_from_db():
    global knowledge_base
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY AUTOINCREMENT, fact TEXT NOT NULL, embedding BLOB)")
        cursor.execute("SELECT id, fact, embedding FROM knowledge")
        rows = cursor.fetchall()

        knowledge_base = []
        for row in rows:
            fact_id = row[0]
            fact_text = row[1]
            embedding_data = row[2]

            if embedding_data:
                embedding = np.frombuffer(embedding_data)  # Десериализуем эмбеддинг из БД
            else:
                # Если эмбеддинг отсутствует, генерируем новый
                embedding = embedding_model.encode(fact_text)
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE knowledge SET embedding = ? WHERE id = ?", (embedding.tobytes(), fact_id))
                    conn.commit()

            knowledge_base.append((fact_id, fact_text, embedding))

# Добавление нового факта с эмбеддингом в базу
def add_fact(fact_text):
    embedding = embedding_model.encode(fact_text)  # Генерация эмбеддинга
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO knowledge (fact, embedding) VALUES (?, ?)", (fact_text, embedding.tobytes()))  # Сохраняем эмбеддинг
        conn.commit()
    load_kb_from_db()

# Обновление факта
def update_fact(fact_id, new_text):
    embedding = embedding_model.encode(new_text)  # Генерация эмбеддинга для нового текста
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE knowledge SET fact = ?, embedding = ? WHERE id = ?", (new_text, embedding.tobytes(), fact_id))
        conn.commit()
    load_kb_from_db()

# Удаление факта
def delete_fact(fact_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge WHERE id = ?", (fact_id,))
        conn.commit()
    load_kb_from_db()

# Векторный поиск
def vector_search(query, top_k=5):
    query_embedding = embedding_model.encode(query)  # Генерация эмбеддинга для запроса
    similarities = []

    # Для каждого факта в базе вычисляем схожесть
    for fact_id, fact_text, fact_embedding in knowledge_base:
        similarity = np.dot(query_embedding, fact_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(fact_embedding))
        similarities.append((fact_id, fact_text, similarity))

    # Сортируем по схожести и возвращаем top_k наиболее похожих фактов
    similarities.sort(key=lambda x: x[2], reverse=True)
    return similarities[:top_k]

# Сброс истории для пользователя
def reset_history(user_id):
    user_histories[user_id] = []

# Обработка запроса к базе знаний и возврат ответа
def query_knowledge(prompt, user_id):
    history = user_histories.get(user_id, [])
    context = "\n".join(f"- {fact[1]}" for fact in knowledge_base)

    system_message = {
        "role": "system",
        "content": (
            "Ты — ассистент, который отвечает строго на основе следующих фактов:\n\n"
            f"{context}\n\n"
            "Если информации недостаточно, честно скажи, что не знаешь."
        )
    }

    messages = [system_message] + history + [{"role": "user", "content": prompt}]
    payload = {
        "model": "mistral",
        "messages": messages,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        data = response.json()
        answer = data.get("message", {}).get("content", "Ошибка получения ответа.")
    except Exception as e:
        answer = f"Ошибка подключения к Ollama: {e}"

    history.append({"role": "user", "content": prompt})
    history.append({"role": "assistant", "content": answer})
    user_histories[user_id] = history[-10:]

    return answer
