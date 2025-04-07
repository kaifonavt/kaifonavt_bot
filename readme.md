




## ⚙️ Настройка

### 1. Установи зависимости

После того как файл `requirements.txt` готов, установи все необходимые библиотеки:

```bash
pip install -r requirements.txt
```

### 2. Создай `.env` файл

В корне проекта создай файл с именем `.env` и добавь в него следующие строки:

```env
BOT_TOKEN=твой_бот_токен_от_BotFather
OLLAMA_API=http://localhost:11434
DEFAULT_MODEL=mistral
```

### 3. Запусти модель через Ollama

```bash
ollama run mistral
```

### 4. Запусти бота

```bash
python ollama_telebot.py
```

---

## 💬 Команды

- `/start` — начать работу
- `/help` — показать справку
- `/model` — выбрать LLM-модель для общения

---
