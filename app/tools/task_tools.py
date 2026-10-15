
from app.task_manager import (
    add_task,
    get_tasks,
    update_task_status,
    update_task_details,
    clear_task_due_date,
    delete_task,
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


def reopen_task_tool(task_id, session_id):
    """Reopen a completed task belonging to the current session."""
    return update_task_status(
        task_id=task_id,
        status="Pending",
        session_id=session_id,
    )


def update_task_tool(
    task_id,
    session_id,
    title=None,
    due_date=None,
    priority=None,
    status=None,
):
    """Update selected fields of a task belonging to the current session."""
    return update_task_details(
        task_id=task_id,
        session_id=session_id,
        title=title,
        due_date=due_date,
        priority=priority,
        status=status,
    )


def clear_task_due_date_tool(task_id, session_id):
    """Remove a task's deadline."""
    return clear_task_due_date(
        task_id=task_id,
        session_id=session_id,
    )


def delete_task_tool(task_id, session_id):
    """Delete a task belonging to the current session."""
    return delete_task(
        task_id=task_id,
        session_id=session_id,
    )
