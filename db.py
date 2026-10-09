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
    cur.execute("CREATE TABLE users (id TEXT PRIMARY KEY, name TEXT, password TEXT, is_admin INTEGER DEFAULT 0)")
    cur.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        [(uid, name, pwd, 1 if uid == "1" else 0) for uid, name, pwd in SEED_USERS],
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


def count_users() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    (total,) = cur.fetchone()
    conn.close()
    return total


def db_stats() -> dict:
    return {"users": count_users(), "db_bytes": os.path.getsize(DB_PATH)}


def init_shop() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS items")
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, total REAL)")
    cur.execute(
        "CREATE TABLE items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, sku TEXT, qty INTEGER)"
    )
    seed = [
        ("1", 42.5), ("1", 9.99), ("2", 100.0), ("2", 15.0),
        ("3", 7.5), ("4", 250.0), ("4", 33.0), ("5", 12.0),
    ]
    cur.executemany("INSERT INTO orders (user_id, total) VALUES (?, ?)", seed)
    cur.executemany(
        "INSERT INTO items (order_id, sku, qty) VALUES (?, ?, ?)",
        [(oid, f"SKU-{oid:03d}", (oid % 3) + 1) for oid in range(1, 9)],
    )
    conn.commit()
    conn.close()


def create_order(user_id: str, total: float) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))
    oid = cur.lastrowid
    conn.commit()
    conn.close()
    return oid


def get_order(order_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, total FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return row


def list_user_orders(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, total FROM orders WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_order_items(order_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, sku, qty FROM items WHERE order_id = ?", (order_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def set_superadmin(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_admin = 2 WHERE id = ?", (user_id,))
    conn.commit()
    cur.execute("SELECT id, name, is_admin FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


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


def verify_user(user_id: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE id = ? AND password = ?", (user_id, password))
    row = cur.fetchone()
    conn.close()
    return row


def update_user(user_id: str, fields: dict):
    allowed = ("name", "password", "is_admin")
    sets = [f"{k} = ?" for k in fields if k in allowed]
    if not sets:
        return None
    vals = [fields[k] for k in fields if k in allowed]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {', '.join(sets)} WHERE id = ?", (*vals, user_id))
    conn.commit()
    cur.execute("SELECT id, name, is_admin FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def search_users(q: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = f"SELECT id, name FROM users WHERE name LIKE '%{q}%'"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows


def count_orders() -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders")
    (total,) = cur.fetchone()
    conn.close()
    return total


def order_revenue() -> float:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(total), 0) FROM orders")
    (total,) = cur.fetchone()
    conn.close()
    return float(total)


def list_orders(limit: int = 50, skip: int = 0):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, total FROM orders ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, skip),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def recent_orders(limit: int = 5):
    return list_orders(limit=limit, skip=0)
