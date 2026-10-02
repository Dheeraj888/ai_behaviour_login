from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DATA_DIR = Path(os.environ.get("BEHAVIOR_AUTH_DATA_DIR") or Path(__file__).parent / "data")
DB_PATH = DATA_DIR / "behavior_auth.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash BLOB NOT NULL,
                pin_hash BLOB NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS behavior_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                typing_duration REAL NOT NULL,
                avg_key_interval REAL NOT NULL,
                backspace_count INTEGER NOT NULL,
                mouse_distance REAL NOT NULL,
                avg_mouse_speed REAL NOT NULL,
                login_hour REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT NOT NULL,
                trust_score REAL,
                prediction TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS pending_challenges (
                challenge_token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                sample_json TEXT NOT NULL,
                trust_score REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
