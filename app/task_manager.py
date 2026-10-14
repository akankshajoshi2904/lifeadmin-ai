
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE = DATA_DIRECTORY / "lifeadmin.db"


def get_connection():
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DATABASE), timeout=30)


def create_tasks_table():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT,
                priority TEXT,
                status TEXT DEFAULT 'Pending'
            )
            """
        )


def task_exists(title, due_date):
    with get_connection() as connection:
        task = connection.execute(
            """
            SELECT id FROM tasks
            WHERE title = ?
              AND due_date IS ?
              AND status = 'Pending'
            LIMIT 1
            """,
            (title, due_date),
        ).fetchone()

    return task is not None


def add_task(title, due_date=None, priority="Low"):
    if task_exists(title, due_date):
        return False

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO tasks (title, due_date, priority)
            VALUES (?, ?, ?)
            """,
            (title, due_date, priority),
        )

    return True


def get_tasks():
    with get_connection() as connection:
        tasks = connection.execute(
            """
            SELECT id, title, due_date, priority, status
            FROM tasks
            ORDER BY
                CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Low' THEN 3
                    ELSE 4
                END,
                CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
                due_date
            """
        ).fetchall()

    return tasks


def update_task_status(task_id, status):
    if status not in ("Pending", "Completed"):
        raise ValueError("Status must be Pending or Completed.")

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET status = ?
            WHERE id = ?
            """,
            (status, task_id),
        )
