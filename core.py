import sqlite3
import numpy as np
import requests
from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434")
DB_PATH = os.getenv("DB_PATH", "knowledge.db")
RESPONSE_MODEL = os.getenv("RESPONSE_MODEL", "llama3:8b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT CHECK(role IN ('user', 'bot')) NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def load_kb_from_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fact FROM knowledge")
        return cursor.fetchall()

def save_message(user_id, role, content):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        conn.commit()

def get_chat_history(user_id, limit=10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM messages
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        history = cursor.fetchall()
        return list(reversed(history))

def generate_embedding(text):
    try:
        response = requests.post(f"{OLLAMA_API}/api/embeddings", json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        })
        response.raise_for_status()
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
        print(f"✅ Факт добавлен: {fact_text}")
    except Exception as e:
        print(f"❌ Ошибка при добавлении факта: {e}")

def update_fact(fact_id, new_text):
    try:
        embedding = generate_embedding(new_text)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE knowledge SET fact = ?, embedding = ? WHERE id = ?", (new_text, embedding.tobytes(), fact_id))
            conn.commit()
        print(f"✅ Факт обновлён: {new_text}")
    except Exception as e:
        print(f"❌ Ошибка при обновлении факта: {e}")

def delete_fact(fact_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM knowledge WHERE id = ?", (fact_id,))
            conn.commit()
        print(f"🗑️ Факт с id {fact_id} удалён.")
    except Exception as e:
        print(f"❌ Ошибка при удалении факта: {e}")

def vector_search(query, top_k=5, similarity_threshold=0.7):
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

    history = get_chat_history(user_id, limit=10)
    history_text = "\n".join(
        f"{'Пользователь' if role == 'user' else 'Ассистент'}: {content}" 
        for role, content in history
    )

    final_prompt = (
        "Ты — вежливый, умный ассистент. Отвечай кратко и по делу.\n"
        "Отвечай на языке вопроса. Учитывай контекст диалога и знания.\n\n"
        f"История диалога:\n{history_text}\n\n"
        f"Актуальные знания:\n{context}\n\n"
        f"Текущий вопрос: {prompt}"
    )

    try:
        response = requests.post(f"{OLLAMA_API}/api/generate", json={
            "model": RESPONSE_MODEL,
            "prompt": final_prompt,
            "stream": False
        })
        response.raise_for_status()
        answer = response.json().get("response", "❌ Ошибка генерации")
        save_message(user_id, "user", prompt)
        save_message(user_id, "bot", answer)
        return answer
    except Exception as e:
        return f"⚠️ Ошибка генерации: {e}"

init_db()
