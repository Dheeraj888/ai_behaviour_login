"""Create 5 demo user accounts (no fake behaviour data).

Run:  python -m app.seed_demo          (skips users that already exist)
      python -m app.seed_demo --reset  (deletes the 5 demo users first, then recreates them)

The accounts start with no behavioural samples and no trained model, so every
login with the right email + password succeeds and records the tester's own
typing/mouse behaviour as a baseline sample. After 5+ logins (or dashboard
"Add Behavior Sample"), open the dashboard and click Train.
"""
from __future__ import annotations
import sys

from .db import init_db, get_conn
from .ml import model_path
from .main import _hash

PASSWORD = "Demo@1234"
PIN = "1234"

USERS = [
    ("Aarav Sharma", "aarav@example.com"),
    ("Priya Singh", "priya@example.com"),
    ("Rohan Verma", "rohan@example.com"),
    ("Neha Gupta", "neha@example.com"),
    ("Karan Mehta", "karan@example.com"),
]


def _delete_user(conn, email):
    row = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if not row:
        return
    uid = row["id"]
    for table in ("behavior_samples", "login_attempts", "sessions", "pending_challenges"):
        conn.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    try:
        model_path(uid).unlink()
    except FileNotFoundError:
        pass


def main():
    init_db()
    if "--reset" in sys.argv:
        with get_conn() as conn:
            for _, email in USERS:
                _delete_user(conn, email)
        print("reset: demo users removed")
    for name, email in USERS:
        with get_conn() as conn:
            if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                print(f"skip   {email} (already exists)")
                continue
            conn.execute("INSERT INTO users(name,email,password_hash,pin_hash) VALUES(?,?,?,?)",
                         (name, email, _hash(PASSWORD), _hash(PIN)))
        print(f"create {email}")
    print(f"\nDone. Password: {PASSWORD}   PIN: {PIN}")


if __name__ == "__main__":
    main()
