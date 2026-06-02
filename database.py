import sqlite3
from datetime import date, datetime
from typing import Optional

DB_PATH = "habits.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            frequency TEXT DEFAULT 'daily' CHECK(frequency IN ('daily', 'weekly')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_date DATE NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE(habit_id, completed_date)
        );
    """)
    conn.commit()
    conn.close()


def register_user(user_id: int, username: Optional[str]) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username),
    )
    conn.commit()
    conn.close()


def add_habit(user_id: int, name: str, description: str, frequency: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO habits (user_id, name, description, frequency) VALUES (?, ?, ?, ?)",
        (user_id, name, description, frequency),
    )
    conn.commit()
    habit_id = cur.lastrowid
    conn.close()
    return habit_id


def get_habits(user_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, description, frequency, created_at FROM habits WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def get_habit(habit_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, user_id, name, description, frequency, created_at FROM habits WHERE id = ?",
        (habit_id,),
    ).fetchone()
    conn.close()
    return row


def update_habit(habit_id: int, name: str, description: str, frequency: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE habits SET name = ?, description = ?, frequency = ? WHERE id = ?",
        (name, description, frequency, habit_id),
    )
    conn.commit()
    conn.close()


def delete_habit(habit_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()


def log_habit(habit_id: int, log_date: date) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO habit_logs (habit_id, completed_date) VALUES (?, ?)",
            (habit_id, log_date.isoformat()),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False


def unlog_habit(habit_id: int, log_date: date) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM habit_logs WHERE habit_id = ? AND completed_date = ?",
        (habit_id, log_date.isoformat()),
    )
    conn.commit()
    conn.close()


def is_habit_completed_today(habit_id: int, today: date) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM habit_logs WHERE habit_id = ? AND completed_date = ?",
        (habit_id, today.isoformat()),
    ).fetchone()
    conn.close()
    return row is not None


def get_habit_logs(habit_id: int, limit: int = 90):
    conn = get_connection()
    rows = conn.execute(
        "SELECT completed_date FROM habit_logs WHERE habit_id = ? ORDER BY completed_date DESC LIMIT ?",
        (habit_id, limit),
    ).fetchall()
    conn.close()
    return [row["completed_date"] for row in rows]


def get_habit_stats(habit_id: int):
    conn = get_connection()
    today = date.today()
    logs = conn.execute(
        "SELECT completed_date FROM habit_logs WHERE habit_id = ? ORDER BY completed_date DESC",
        (habit_id,),
    ).fetchall()
    habit = conn.execute(
        "SELECT frequency, created_at FROM habits WHERE id = ?", (habit_id,)
    ).fetchone()
    conn.close()

    if not habit:
        return None

    completed_dates = {row["completed_date"] for row in logs}
    return {
        "frequency": habit["frequency"],
        "created_at": habit["created_at"],
        "completed_dates": completed_dates,
    }
