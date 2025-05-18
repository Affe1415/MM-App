import sqlite3

DB_NAME = 'email_templates.db'

def connect():
    conn = sqlite3.connect(DB_NAME)
    return conn

def setup_database():
    conn = connect()
    cursor = conn.cursor()

    # Rätta och kompletta CREATE-satser
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES categories(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')

    conn.commit()
    conn.close()
