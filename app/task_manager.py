
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE = DATA_DIRECTORY / "lifeadmin.db"


def get_connection():
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE), timeout=30)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tasks_table():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT,
                priority TEXT,
                status TEXT DEFAULT 'Pending',
                session_id TEXT
            )
            """
        )

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(tasks)"
            ).fetchall()
        }

        if "session_id" not in columns:
            connection.execute(
                "ALTER TABLE tasks ADD COLUMN session_id TEXT"
            )


def _require_session_id(session_id):
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("A valid session ID is required.")
    return session_id


def task_exists(title, due_date, session_id):
    session_id = _require_session_id(session_id)

    with get_connection() as connection:
        task = connection.execute(
            """
            SELECT id
            FROM tasks
            WHERE title = ?
              AND due_date IS ?
              AND status = 'Pending'
              AND session_id = ?
            LIMIT 1
            """,
            (title, due_date, session_id),
        ).fetchone()

    return task is not None


def add_task(title, due_date=None, priority="Low", session_id=None):
    session_id = _require_session_id(session_id)

    if task_exists(title, due_date, session_id):
        return False

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tasks (title, due_date, priority, session_id)
            VALUES (?, ?, ?, ?)
            """,
            (title, due_date, priority, session_id),
        )

    return True


def get_tasks(session_id):
    session_id = _require_session_id(session_id)

    with get_connection() as connection:
        tasks = connection.execute(
            """
            SELECT id, title, due_date, priority, status
            FROM tasks
            WHERE session_id = ?
            ORDER BY
                CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Low' THEN 3
                    ELSE 4
                END,
                CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
                due_date
            """,
            (session_id,),
        ).fetchall()

    return tasks


def update_task_status(task_id, status, session_id):
    session_id = _require_session_id(session_id)

    if status not in ("Pending", "Completed"):
        raise ValueError("Status must be Pending or Completed.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = ?
            WHERE id = ?
              AND session_id = ?
            """,
            (status, task_id, session_id),
        )

    return cursor.rowcount == 1
