import sqlite3


DATABASE = "data/lifeadmin.db"


def create_tasks_table():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    connection.commit()
    connection.close()


def task_exists(title, due_date):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM tasks
        WHERE title = ?
        AND due_date = ?
        AND status = 'Pending'
    """, (title, due_date))

    task = cursor.fetchone()

    connection.close()

    return task is not None


def add_task(title, due_date=None, priority="Low"):

    if task_exists(title, due_date):
        return False

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, due_date, priority)
        VALUES (?, ?, ?)
    """, (title, due_date, priority))

    connection.commit()
    connection.close()

    return True


def get_tasks():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, due_date, priority, status
        FROM tasks
        ORDER BY
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END,
            due_date
    """)

    tasks = cursor.fetchall()

    connection.close()

    return tasks


def update_task_status(task_id, status):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (status, task_id))

    connection.commit()
    connection.close()