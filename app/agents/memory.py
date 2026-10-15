
from app.task_manager import get_tasks


def get_memory(session_id):
    """Retrieve only tasks belonging to the current session."""

    tasks = get_tasks(session_id=session_id)
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
