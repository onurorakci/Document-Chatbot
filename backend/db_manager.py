import sqlite3
import json
import random
import string
import os

# Custom database manager for storing chat contexts and histories using SQLite, 
# with functions to save and retrieve chat data based on unique chat IDs. 
# Each chat session is stored in a separate database file to ensure isolation 
# and efficient retrieval of context and history for each user interaction.
def generate_db_name():
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"chat_history_{rand_str}.db"

DB_NAME = generate_db_name()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)  # Delete DB


    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS chats 
                     (chat_id TEXT PRIMARY KEY, context TEXT, history TEXT)''')
        conn.commit()

init_db()

def save_chat(chat_id, context=None, history=None):
    with get_db() as conn:
        if context is not None:
            conn.execute("INSERT INTO chats (chat_id, context, history) VALUES (?, ?, ?) ON CONFLICT(chat_id) DO UPDATE SET context=?", (chat_id, context, "[]", context))
        if history is not None:
            conn.execute("UPDATE chats SET history=? WHERE chat_id=?", (json.dumps(history), chat_id))
        conn.commit()

def get_chat_data(chat_id):
    with get_db() as conn:
        row = conn.execute("SELECT context, history FROM chats WHERE chat_id=?", (chat_id,)).fetchone()
        return (row['context'], json.loads(row['history'])) if row else (None, [])