# backend/user_db.py
import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent / "users.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Creates DB if missing, and ensures schema exists.
    Automatically inserts admin user if table is empty.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Create base users table (clean schema, no email verify stuff)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        sec_q1 TEXT,
        sec_q2 TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    conn.commit()

    # ✅ Check if table is empty → insert default admin
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("""
            INSERT INTO users (username, password, email, is_admin)
            VALUES ('admin', 'admin123', 'admin@local', 1)
        """)
        conn.commit()
        print("✅ Created default admin user: admin / admin123")
    else:
        print("✅ users.db loaded — existing users found")

    conn.close()


def create_user(username, password, email=None, sec_q1=None, sec_q2=None, is_admin=0):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, password, email, sec_q1, sec_q2, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password, email, sec_q1, sec_q2, is_admin))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_password(username, plain_password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] == plain_password  # ✅ simple string compare


def get_user_by_username(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, sec_q1, sec_q2, is_admin FROM users WHERE username = ?", (username,))
    r = cur.fetchone()
    conn.close()
    if not r: 
        return None
    return {
        "id": r[0],
        "username": r[1],
        "email": r[2],
        "sec_q1": r[3],
        "sec_q2": r[4],
        "is_admin": bool(r[5])
    }


def update_password(username, new_password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()


def list_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, is_admin FROM users")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "username": r[1], "email": r[2], "is_admin": bool(r[3])} for r in rows]


def is_admin(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    r = cur.fetchone()
    conn.close()
    return bool(r and r[0] == 1)
