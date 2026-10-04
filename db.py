import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

SEED_USERS = [
    ("1", "alice", "alice123"),
    ("2", "bob", "bob123"),
    ("3", "carol", "carol123"),
    ("4", "dave", "dave123"),
    ("5", "erin", "erin123"),
]


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users (id TEXT PRIMARY KEY, name TEXT, password TEXT)")
    cur.executemany("INSERT INTO users VALUES (?, ?, ?)", SEED_USERS)
    conn.commit()
    conn.close()


def get_user(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, password FROM users WHERE id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def count_users() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    (total,) = cur.fetchone()
    conn.close()
    return total


def list_users(limit: int = 20, skip: int = 0, sort: str = "id"):
    col = sort if sort in ("id", "name") else "id"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        f"SELECT id, name FROM users ORDER BY {col} LIMIT ? OFFSET ?",
        (limit, skip),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def search_users(q: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = f"SELECT id, name FROM users WHERE name LIKE '%{q}%'"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows
