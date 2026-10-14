
from datetime import datetime

from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.router import detect_intent
from app.agents.task_parser import extract_task_title
from app.agents.task_date_parser import extract_due_date
from app.agents.memory import get_memory
from app.tools.task_tools import (
    create_task_tool,
    complete_task_tool,
)


def detect_intent_node(state: AgentState):
    """Detect the user's intent."""
    state.intent = detect_intent(state.user_request)
    state.current_step = "Intent detected"
    return state


def get_tasks_node(state: AgentState):
    """Retrieve saved tasks through the memory layer."""
    state.tasks = get_memory()
    state.current_step = "Tasks retrieved from memory"
    return state


def prioritize_tasks_node(state: AgentState):
    """Prioritize pending tasks using priority and deadline."""
    today = datetime.now()
    prioritized_tasks = []

    for task in state.tasks:
        if isinstance(task, dict):
            task_id = task["id"]
            title = task["title"]
            due_date = task["due_date"]
            priority = task["priority"]
            status = task["status"]
        else:
            task_id, title, due_date, priority, status = task

        if status != "Pending":
            continue

        try:
            due = datetime.strptime(due_date, "%d %B %Y")
            days_left = (due.date() - today.date()).days
        except (ValueError, TypeError):
            days_left = 9999

        if days_left < 0:
            urgency = "Overdue"
        elif days_left <= 7:
            urgency = "Due Soon"
        elif days_left <= 30:
            urgency = "Upcoming"
        else:
            urgency = "Later"

        prioritized_tasks.append({
            "id": task_id,
            "title": title,
            "due_date": due_date,
            "priority": priority,
            "status": status,
            "days_left": days_left,
            "urgency": urgency,
        })

    prioritized_tasks.sort(
        key=lambda task: (
            task["days_left"],
            task["priority"] != "High",
        )
    )

    state.tasks = prioritized_tasks
    state.current_step = "Tasks prioritized"
    return state


def plan_next_action_node(state: AgentState):
    """Create an ordered plan based on the user's intent."""
    if state.intent == "create_task":
        task_title = extract_task_title(state.user_request)
        due_date = extract_due_date(state.user_request)

        if due_date:
            state.plan = [
                f"Create task: {task_title} — Due: {due_date}"
            ]
        else:
            state.plan = [f"Create task: {task_title}"]

        state.current_step = "Plan created"
        return state

    if not state.tasks:
        state.plan = []
        state.current_step = "Plan created"
        return state

    state.plan = [task["title"] for task in state.tasks]
    state.current_step = "Plan created"
    return state


def prepare_execution_node(state: AgentState):
    """Require approval before modifying tasks."""
    if state.intent in ["upcoming_tasks", "review_tasks"]:
        state.approval_required = False
        state.current_step = "Information ready"
        return state

    if state.intent == "create_task":
        state.approval_required = True
        state.response = (
            "A new task is ready to be created. "
            "Human approval is required before creation."
        )
        state.current_step = "Waiting for approval"
        return state

    if not state.tasks:
        state.approval_required = False
        state.current_step = "No action available"
        return state

    next_task = state.tasks[0]
    state.approval_required = True
    state.response = (
        f"Execution prepared for task {next_task['id']}: "
        f"{next_task['title']}. "
        "Human approval is required before execution."
    )
    state.current_step = "Waiting for approval"
    return state


def execute_task_node(state: AgentState):
    """Execute task actions only after approval."""
    if state.intent in ["upcoming_tasks", "review_tasks"]:
        state.current_step = "Information only"
        return state

    if not state.approval_required or not state.approved:
        state.current_step = "Execution blocked"
        return state

    if state.intent == "create_task":
        task_title = extract_task_title(state.user_request)
        due_date = extract_due_date(state.user_request)

        created = create_task_tool(
            title=task_title,
            due_date=due_date,
            priority="Medium",
        )

        if created:
            if due_date:
                state.response = (
                    f"Task created successfully: {task_title}. "
                    f"Due date: {due_date}."
                )
            else:
                state.response = (
                    f"Task created successfully: {task_title}."
                )
        else:
            state.response = f"The task already exists: {task_title}."

        state.approval_required = False
        state.approved = False
        state.current_step = "Task executed"
        return state

    if not state.tasks:
        state.current_step = "No action available"
        return state

    next_task = state.tasks[0]
    complete_task_tool(next_task["id"])

    state.approval_required = False
    state.approved = False
    state.response = (
        f"Task completed successfully: {next_task['title']}."
    )
    state.current_step = "Task executed"
    return state


def summarize_tasks_node(state: AgentState):
    """Create a response based on the user's intent."""
    if state.intent == "create_task":
        if state.current_step == "Execution blocked":
            task_title = extract_task_title(state.user_request)
            due_date = extract_due_date(state.user_request)

            if due_date:
                state.response = (
                    f"Task ready to create: {task_title}. "
                    f"Due date: {due_date}. "
                    "Human approval is required before creation."
                )
            else:
                state.response = (
                    f"Task ready to create: {task_title}. "
                    "Human approval is required before creation."
                )
        return state

    if not state.tasks:
        state.response = "You have no pending tasks."

    elif state.intent == "upcoming_tasks":
        upcoming_tasks = [
            task for task in state.tasks
            if task["urgency"] in ["Upcoming", "Due Soon", "Overdue"]
        ]

        if upcoming_tasks:
            task_lines = [
                f"{task['title']} — Due: {task['due_date']} "
                f"({task['urgency']})"
                for task in upcoming_tasks
            ]
            state.response = (
                "Here are your upcoming tasks:\n"
                + "\n".join(task_lines)
            )
        else:
            state.response = "You have no upcoming tasks."

    elif state.intent == "review_tasks":
        due_soon = [
            task for task in state.tasks
            if task["urgency"] in ["Overdue", "Due Soon"]
        ]
        high_priority = [
            task for task in state.tasks
            if task["priority"] == "High"
        ]
        next_action = state.plan[0]

        state.response = (
            f"You have {len(state.tasks)} pending task(s). "
            f"{len(high_priority)} are high priority. "
            f"{len(due_soon)} need attention within the next 7 days. "
            f"Your next action should be: {next_action}."
        )

    elif state.current_step == "Execution blocked":
        due_soon = [
            task for task in state.tasks
            if task["urgency"] in ["Overdue", "Due Soon"]
        ]
        high_priority = [
            task for task in state.tasks
            if task["priority"] == "High"
        ]
        next_action = state.plan[0]

        state.response = (
            f"You have {len(state.tasks)} pending task(s). "
            f"{len(high_priority)} are high priority. "
            f"{len(due_soon)} need attention within the next 7 days. "
            f"Your next action should be: {next_action}. "
            "Human approval is required before execution."
        )

    elif state.current_step == "Task executed":
        state.response = (
            "Task executed successfully. "
            f"The completed action was: {state.plan[0]}."
        )

    else:
        due_soon = [
            task for task in state.tasks
            if task["urgency"] in ["Overdue", "Due Soon"]
        ]
        high_priority = [
            task for task in state.tasks
            if task["priority"] == "High"
        ]
        next_action = state.plan[0]

        state.response = (
            f"You have {len(state.tasks)} pending task(s). "
            f"{len(high_priority)} are high priority. "
            f"{len(due_soon)} need attention within the next 7 days. "
            f"Your next action should be: {next_action}. "
            "Human approval is required before execution."
        )

    state.current_step = "Tasks summarized"
    return state


def route_by_intent(state: AgentState):
    """Choose the workflow path based on detected intent."""
    if state.intent == "complete_task":
        return "complete_task"
    if state.intent == "upcoming_tasks":
        return "upcoming_tasks"
    if state.intent == "create_task":
        return "create_task"
    return "review_tasks"


graph = StateGraph(AgentState)

graph.add_node("detect_intent", detect_intent_node)
graph.add_node("get_tasks", get_tasks_node)
graph.add_node("prioritize_tasks", prioritize_tasks_node)
graph.add_node("plan_next_action", plan_next_action_node)
graph.add_node("prepare_execution", prepare_execution_node)
graph.add_node("execute_task", execute_task_node)
graph.add_node("summarize_tasks", summarize_tasks_node)

graph.add_edge(START, "detect_intent")

graph.add_conditional_edges(
    "detect_intent",
    route_by_intent,
    {
        "complete_task": "get_tasks",
        "upcoming_tasks": "get_tasks",
        "create_task": "get_tasks",
        "review_tasks": "get_tasks",
    },
)

graph.add_edge("get_tasks", "prioritize_tasks")
graph.add_edge("prioritize_tasks", "plan_next_action")
graph.add_edge("plan_next_action", "prepare_execution")
graph.add_edge("prepare_execution", "execute_task")
graph.add_edge("execute_task", "summarize_tasks")
graph.add_edge("summarize_tasks", END)

lifeadmin_agent = graph.compile()
