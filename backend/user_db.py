# backend/user_db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

def get_connection():
    conn = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
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
    conn.commit()

    # Default admin
    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (username, password, is_admin)
            VALUES (%s, %s, TRUE)
        """, ("admin", generate_password_hash("admin123")))
        conn.commit()
        print("✅ Created default admin user: admin / admin123")

    cur.close()
    conn.close()

def create_user(username, password, email=None, sec_q1=None, sec_q2=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, password, email, sec_q1, sec_q2)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, generate_password_hash(password), email, sec_q1, sec_q2))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Error creating user:", e)
        return False

def verify_password(username, password):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT password FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row and check_password_hash(row["password"], password)

def list_users():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, email, is_admin FROM users ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row
