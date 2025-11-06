# backend/user_db.py

import os
import sqlite3
import psycopg2
from urllib.parse import urlparse
from pathlib import Path

# -------------------- DATABASE CONFIG --------------------
DATABASE_URL = os.environ.get("DATABASE_URL")  # Set by Railway
IS_POSTGRES = DATABASE_URL is not None

if IS_POSTGRES:
    parsed = urlparse(DATABASE_URL)
    PG_CONN = {
        "dbname": parsed.path[1:],
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port,
    }
else:
    DB_PATH = str(Path(__file__).resolve().parent / "users.db")


# -------------------- CONNECTION HANDLER --------------------
def get_conn():
    if IS_POSTGRES:
        return psycopg2.connect(**PG_CONN)
    return sqlite3.connect(DB_PATH)


# -------------------- INITIALIZE DB --------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    if IS_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                sec_q1 TEXT,
                sec_q2 TEXT,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
    else:
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

    # ✅ Create default admin if empty
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count == 0:
        if IS_POSTGRES:
            cur.execute("""
                INSERT INTO users (username, password, email, is_admin)
                VALUES (%s, %s, %s, %s)
            """, ('admin', 'admin123', 'admin@local', True))
        else:
            cur.execute("""
                INSERT INTO users (username, password, email, is_admin)
                VALUES (?, ?, ?, ?)
            """, ('admin', 'admin123', 'admin@local', 1))
        conn.commit()
        print("✅ Created default admin user: admin / admin123")
    else:
        print("✅ Database loaded — users found")

    cur.close()
    conn.close()


# -------------------- CRUD FUNCTIONS --------------------
def create_user(username, password, email=None, sec_q1=None, sec_q2=None, is_admin=False):
    conn = get_conn()
    cur = conn.cursor()
    try:
        if IS_POSTGRES:
            cur.execute("""
                INSERT INTO users (username, password, email, sec_q1, sec_q2, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, password, email, sec_q1, sec_q2, is_admin))
        else:
            cur.execute("""
                INSERT INTO users (username, password, email, sec_q1, sec_q2, is_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password, email, sec_q1, sec_q2, is_admin))
        conn.commit()
        return True
    except Exception as e:
        print("⚠️ Create user failed:", e)
        return False
    finally:
        conn.close()


def verify_password(username, plain_password):
    conn = get_conn()
    cur = conn.cursor()
    try:
        if IS_POSTGRES:
            cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        else:
            cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return row and row[0] == plain_password
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_conn()
    cur = conn.cursor()
    try:
        if IS_POSTGRES:
            cur.execute("SELECT id, username, email, sec_q1, sec_q2, is_admin FROM users WHERE username = %s", (username,))
        else:
            cur.execute("SELECT id, username, email, sec_q1, sec_q2, is_admin FROM users WHERE username = ?", (username,))
        r = cur.fetchone()
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
    finally:
        conn.close()


def update_password(username, new_password):
    conn = get_conn()
    cur = conn.cursor()
    if IS_POSTGRES:
        cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
    else:
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
    if IS_POSTGRES:
        cur.execute("SELECT is_admin FROM users WHERE username = %s", (username,))
    else:
        cur.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    r = cur.fetchone()
    conn.close()
    return bool(r and r[0])
