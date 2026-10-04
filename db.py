import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users (id TEXT PRIMARY KEY, name TEXT, password TEXT)")
    cur.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [("1", "alice", "alice123"), ("2", "bob", "bob123")],
    )
    conn.commit()
    conn.close()


def get_user(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, password FROM users WHERE id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
