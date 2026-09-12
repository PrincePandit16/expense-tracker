import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Opens a connection to the SQLite database and configures it.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates the users and expenses tables if they do not exist.
    """
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()

def seed_db():
    """
    Populates the database with demo data if it's empty.
    """
    with get_db() as conn:
        # Check if users table already contains data
        user_exists = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if user_exists:
            return

        # Insert demo user
        demo_password = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", demo_password)
        )
        user_id = cursor.lastrowid

        # Fixed categories from spec
        categories = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

        # Sample expenses (8 total, covering all categories)
        expenses = [
            (user_id, 25.50, "Food", "2023-10-01", "Lunch at Cafe"),
            (user_id, 15.00, "Transport", "2023-10-02", "Uber to office"),
            (user_id, 120.00, "Bills", "2023-10-03", "Electricity bill"),
            (user_id, 45.00, "Health", "2023-10-04", "Pharmacy"),
            (user_id, 60.00, "Entertainment", "2023-10-05", "Movie ticket"),
            (user_id, 110.00, "Shopping", "2023-10-06", "New sneakers"),
            (user_id, 10.00, "Other", "2023-10-07", "Miscellaneous"),
            (user_id, 30.00, "Food", "2023-10-08", "Dinner with friends"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
