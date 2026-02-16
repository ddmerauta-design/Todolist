import sqlite3

# This separates the config from the code
DB_NAME = "todo.db"

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name (row['title'])
    return conn

def init_db():
    """Creates the table if it doesn't exist."""
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                contents TEXT,
                priority TEXT,
                completed BOOLEAN,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
    conn.close()