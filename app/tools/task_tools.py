from task_manager import (
    add_task,
    get_tasks,
    update_task_status,
)


def create_task_tool(title, due_date=None, priority="Low"):
    """
    Create a new task for the user.

    Returns True if a new task was created.
    Returns False if the task already exists.
    """

    return add_task(
        title=title,
        due_date=due_date,
        priority=priority,
    )


def list_tasks_tool():
    """
    Retrieve all tasks stored in LifeAdmin AI.
    """

    return get_tasks()


def complete_task_tool(task_id):
    """
    Mark a task as completed.
    """

    update_task_status(
        task_id=task_id,
        status="Completed",
    )

    return True