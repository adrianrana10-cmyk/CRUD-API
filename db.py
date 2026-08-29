import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = psycopg.connect(DATABASE_URL)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                [("Buy milk", False), ("Walk the dog", True), ("Write report", False)]
            )
    conn.commit()
    conn.close()