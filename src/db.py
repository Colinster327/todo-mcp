import sqlite3


# Database setup
DB_PATH = "db.sqlite3"


def init_database():
    """Initialize the SQLite database with the todos table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))
        )
    ''')

    conn.commit()
    conn.close()


def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)
