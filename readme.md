# Telegram Bot with Local LLM and Knowledge Base

## 🚀 Быстрый старт

### 1. Установка
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка окружения
Создай файл `.env` на основе `.env.example` и укажи:
```env
BOT_TOKEN=your_telegram_token
OLLAMA_API=http://localhost:11434/api
DEFAULT_MODEL=mistral
```

### 3. Инициализация базы данных
```bash
python db.py
```

### 4. Запуск GUI для управления БД
```bash
python gui_db_manager.py
```

## 📘 Команды бота
- `/addfact title | content` — добавить/обновить факт
- `/delfact title` — удалить факт
- `/listfacts` — показать базу знаний
- `/reset` — очистить историю пользователя
