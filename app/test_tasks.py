from task_manager import create_tasks_table, add_task, get_tasks


create_tasks_table()

add_task(
    title="Renew insurance policy",
    due_date="14 October 2026",
    priority="High"
)

tasks = get_tasks()

for task in tasks:
    print(task)