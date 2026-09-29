from datetime import datetime

from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.router import detect_intent
from app.tools.task_tools import (
    list_tasks_tool,
    complete_task_tool,
)


def detect_intent_node(state: AgentState):
    """Detect the user's intent using the separate router module."""
    state.intent = detect_intent(state.user_request)
    state.current_step = "Intent detected"

    return state


def get_tasks_node(state: AgentState):
    """Retrieve the user's tasks."""
    tasks = list_tasks_tool()

    state.tasks = tasks
    state.current_step = "Tasks retrieved"

    return state


def prioritize_tasks_node(state: AgentState):
    """Prioritize pending tasks based on priority and deadline."""
    today = datetime.now()

    prioritized_tasks = []

    for task in state.tasks:
        task_id = task[0]
        title = task[1]
        due_date = task[2]
        priority = task[3]
        status = task[4]

        if status != "Pending":
            continue

        try:
            due = datetime.strptime(due_date, "%d %B %Y")
            days_left = (due - today).days
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
            task["priority"] != "High"
        )
    )

    state.tasks = prioritized_tasks
    state.current_step = "Tasks prioritized"

    return state


def plan_next_action_node(state: AgentState):
    """Create an ordered plan from the prioritized tasks."""
    if not state.tasks:
        state.plan = []
        state.current_step = "Plan created"
        return state

    state.plan = [
        task["title"]
        for task in state.tasks
    ]

    state.current_step = "Plan created"

    return state


def prepare_execution_node(state: AgentState):
    """Prepare the highest-priority task for human approval."""
    if not state.tasks:
        state.approval_required = False
        state.current_step = "No action available"
        return state

    next_task = state.tasks[0]

    state.approval_required = True

    state.response = (
        f"Execution prepared for task {next_task['id']}: "
        f"{next_task['title']}. "
        f"Human approval is required before execution."
    )

    state.current_step = "Waiting for approval"

    return state


def execute_task_node(state: AgentState):
    """Execute the planned task only after human approval."""
    if not state.tasks:
        state.current_step = "No action available"
        return state

    if not state.approval_required or not state.approved:
        state.current_step = "Execution blocked"
        return state

    next_task = state.tasks[0]
    task_id = next_task["id"]

    complete_task_tool(task_id)

    state.approval_required = False
    state.approved = False

    state.response = (
        f"Task completed successfully: "
        f"{next_task['title']}."
    )

    state.current_step = "Task executed"

    return state


def summarize_tasks_node(state: AgentState):
    """Create a summary from the prioritized tasks and plan."""
    if not state.tasks:
        state.response = "You have no pending tasks."

    elif state.current_step == "Execution blocked":
        due_soon = [
            task
            for task in state.tasks
            if task["urgency"] in ["Overdue", "Due Soon"]
        ]

        high_priority = [
            task
            for task in state.tasks
            if task["priority"] == "High"
        ]

        next_action = state.plan[0]

        state.response = (
            f"You have {len(state.tasks)} pending task(s). "
            f"{len(high_priority)} are high priority. "
            f"{len(due_soon)} need attention within the next 7 days. "
            f"Your next action should be: {next_action}. "
            f"Human approval is required before execution."
        )

    elif state.current_step == "Task executed":
        state.response = (
            f"Task executed successfully. "
            f"The completed action was: {state.plan[0]}."
        )

    else:
        due_soon = [
            task
            for task in state.tasks
            if task["urgency"] in ["Overdue", "Due Soon"]
        ]

        high_priority = [
            task
            for task in state.tasks
            if task["priority"] == "High"
        ]

        next_action = state.plan[0]

        state.response = (
            f"You have {len(state.tasks)} pending task(s). "
            f"{len(high_priority)} are high priority. "
            f"{len(due_soon)} need attention within the next 7 days. "
            f"Your next action should be: {next_action}. "
            f"Human approval is required before execution."
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