
from app.task_manager import get_tasks


def get_memory():
    """Retrieve saved tasks as the agent's memory."""

    tasks = get_tasks()
    memory = []

    for task in tasks:
        memory.append({
            "id": task[0],
            "title": task[1],
            "due_date": task[2],
            "priority": task[3],
            "status": task[4],
        })

    return memory
