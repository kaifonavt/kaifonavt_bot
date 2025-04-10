```markdown
# Telegram Knowledge Base Bot

This project is a Telegram bot that manages a knowledge base, allowing users to add, update, delete, and search facts using vector search. The bot interacts with the knowledge base stored in an SQLite database, and it uses embeddings generated via the Ollama API to handle search queries.

## Features:
- **Add Facts**: Add new facts to the knowledge base.
- **Update Facts**: Modify existing facts.
- **Delete Facts**: Remove facts from the knowledge base.
- **Search Facts**: Perform a similarity-based search for facts in the knowledge base.
- **Interactive Buttons**: The bot includes interactive buttons to access the creator's Telegram and external websites.

## Requirements:
- Python 3.x
- `requests` (for making API requests)
- `sqlite3` (for the database)
- `python-dotenv` (for managing environment variables)
- `telebot` (for the Telegram bot)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-knowledge-base-bot.git
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables in a `.env` file:
   ```ini
   TELEGRAM_TOKEN=your_telegram_bot_token  # Telegram bot token
   OLLAMA_API=http://localhost:11434  # URL to the Ollama API
   DB_PATH=knowledge.db  # Path to the SQLite database
   DEFAULT_MODEL=mistral  # Default model for generating embeddings
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

Once the bot is running, users can interact with it via Telegram.

### Commands:
- **/start or /help**: Display a welcome message with a list of available commands.
- **/info**: Provides buttons to:
  - Contact the creator via Telegram
  - Visit external websites
- **Any text message**: The bot will attempt to generate a response based on the knowledge base.

### Bot Actions:
1. **Adding Facts**: Users can add new facts by sending a message to the bot. The bot will generate an embedding for the fact and store it in the database.
2. **Updating Facts**: Users can send a message to modify existing facts. The bot will update the fact in the database and regenerate its embedding.
3. **Deleting Facts**: Users can request to delete a specific fact from the knowledge base.
4. **Searching Facts**: When a user sends a query, the bot uses vector search to find similar facts and returns the most relevant ones.

### Bot Responses:
- The bot generates responses based on the knowledge base and includes only facts relevant to the user's query.
- When a user sends a command, like `/info`, the bot sends interactive buttons to provide more options.
  
### Example:
1. **Add a Fact**: 
   - User: "What is the capital of France?"
   - Bot: "The capital of France is Paris."
   - The bot saves this fact to the database.

2. **Search for Facts**:
   - User: "What are the main cities in France?"
   - Bot: The bot searches the knowledge base for similar facts and provides the most relevant answer.

### Code Structure:

#### `core.py`:
- **Database Management**: Functions for managing the SQLite database (`init_db`, `get_db_connection`).
- **Embedding Generation**: Functions for generating embeddings using the Ollama API (`generate_embedding`).
- **Fact Management**: Functions for adding, updating, deleting, and searching facts in the database (`add_fact`, `update_fact`, `delete_fact`, `vector_search`).
- **Response Generation**: Generates a response based on the knowledge base using the vector search results (`generate_response`).

#### `bot.py` (Main Bot):
- **Telegram Bot**: The main bot logic is handled using the `telebot` library. The bot listens for commands and user messages and responds accordingly.
- **Interactive Buttons**: The bot includes buttons for interacting with external resources like the creator's Telegram and external websites.
- **Message Handling**: The bot handles various commands such as `/start`, `/help`, and `/info`, and listens to user messages to provide appropriate responses based on the knowledge base.

### Error Handling and Feedback:
- **Empty Input**: If the input is empty when adding or updating a fact, the bot will reply with an error message.
- **No Selection for Update/Delete**: If no fact is selected for updating or deleting, a warning message will be shown.
- **Confirmation for Deletion**: When deleting a fact, the bot will confirm the action with the user to avoid accidental deletions.

### Example of the Bot in Action:
- **User**: `/start`
  - **Bot**: "Hello! I am a knowledge base bot. I can help you with facts stored in my database."
- **User**: `/info`
  - **Bot**: Sends interactive buttons for contacting the creator or visiting external websites.
- **User**: "What is the capital of France?"
  - **Bot**: "The capital of France is Paris." (Returns the stored fact if available)

## Improvements and Features in the Future:
- **Better Search Algorithms**: Enhancing the vector search with more advanced techniques, such as approximate nearest neighbors (ANN).
- **More Interactive Features**: Adding new buttons or commands for additional bot functionality, such as browsing or sharing facts.
- **Error Logging**: Implementing better error logging to track and fix issues quickly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### Key Changes:
- **Bot-Specific Content**: Focused on explaining how the bot operates and interacts with users, providing detailed descriptions of the `/start`, `/help`, and `/info` commands.
- **Environment Variables**: The README emphasizes the setup for the Telegram bot token and Ollama API.
- **Code Structure**: Highlighted the separation between `core.py` (which handles the database and logic) and `bot.py` (which implements the bot using `telebot`).
- **Error Handling**: Explained the error handling processes for various user interactions (empty input, no selection, confirmation dialogs).