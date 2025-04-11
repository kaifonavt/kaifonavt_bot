import sqlite3
import numpy as np
import requests
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")
DB_PATH = os.getenv("DB_PATH", "knowledge.db")
MODEL = os.getenv("DEFAULT_MODEL", "mistral")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT NOT NULL,
                embedding BLOB
            )
        ''')
        conn.commit()

def load_kb_from_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fact FROM knowledge")
        return cursor.fetchall()

def generate_embedding(text):
    try:
        response = requests.post(f"{OLLAMA_API}/api/embeddings", json={
            "model": MODEL,
            "prompt": text
        })
        data = response.json()
        return np.array(data["embedding"], dtype=np.float32)
    except Exception as e:
        raise RuntimeError(f"Ошибка генерации эмбеддинга: {e}")

def add_fact(fact_text):
    try:
        embedding = generate_embedding(fact_text)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO knowledge (fact, embedding) VALUES (?, ?)", (fact_text, embedding.tobytes()))
            conn.commit()
        print(f"Факт добавлен: {fact_text}")
    except Exception as e:
        print(f"Ошибка при добавлении факта: {e}")

def update_fact(fact_id, new_text):
    try:
        embedding = generate_embedding(new_text)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE knowledge SET fact = ?, embedding = ? WHERE id = ?", (new_text, embedding.tobytes(), fact_id))
            conn.commit()
        print(f"Факт обновлён: {new_text}")
    except Exception as e:
        print(f"Ошибка при обновлении факта: {e}")


def delete_fact(fact_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM knowledge WHERE id = ?", (fact_id,))
            conn.commit()
        print(f"Факт с id {fact_id} удалён.")
    except Exception as e:
        print(f"Ошибка при удалении факта: {e}")

def vector_search(query, top_k=5, similarity_threshold=0.5):
    query_vec = generate_embedding(query)
    results = []

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fact, embedding FROM knowledge")
        for row in cursor.fetchall():
            fact_id, fact_text, emb_bytes = row
            fact_vec = np.frombuffer(emb_bytes, dtype=np.float32)
            similarity = np.dot(query_vec, fact_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(fact_vec))

            if similarity >= similarity_threshold:
                results.append((fact_id, fact_text, similarity))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]

def generate_response(user_id, prompt):
    context_facts = vector_search(prompt)
    context = "\n".join(f"- {fact[1]}" for fact in context_facts)

    final_prompt = (
        "Ты — вежливый ассистент. Отвечай кратко и по делу.\n"
        "Не отвечай то о чем не спросил пользователь.\n"
        "Отвечай на языке вопроса.\n"
        "Используй только эти факты, которые относятся к тебе, если они отоносятся к вопросу:\n"
        f"{context}\n\n"
        f"Вопрос: {prompt}"
    )

    try:
        response = requests.post(f"{OLLAMA_API}/api/generate", json={
            "model": MODEL,
            "prompt": final_prompt,
            "stream": False
        })
        return response.json().get("response", "❌ Ошибка генерации")
    except Exception as e:
        return f"⚠️ Ошибка при обращении к Ollama: {e}"

init_db()
