
from app.task_manager import (
    add_task,
    get_tasks,
    update_task_status,
)


def create_task_tool(title, due_date=None, priority="Low", session_id=None):
    """Create a task belonging to the current session."""

    return add_task(
        title=title,
        due_date=due_date,
        priority=priority,
        session_id=session_id,
    )


def list_tasks_tool(session_id):
    """Retrieve tasks belonging to the current session."""

    return get_tasks(session_id=session_id)


def complete_task_tool(task_id, session_id):
    """Complete a task only if it belongs to the current session."""

    return update_task_status(
        task_id=task_id,
        status="Completed",
        session_id=session_id,
    )
