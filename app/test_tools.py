from tools.task_tools import (
    create_task_tool,
    list_tasks_tool,
    complete_task_tool,
)


# Test 1: Create a task
created = create_task_tool(
    title="Submit college assignment",
    due_date="30 September 2026",
    priority="Medium",
)

print("Task created:", created)


# Test 2: List tasks
tasks = list_tasks_tool()

print("\nCurrent tasks:")

for task in tasks:
    print(task)