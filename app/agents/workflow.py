from datetime import datetime

from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.tools.task_tools import list_tasks_tool


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


def summarize_tasks_node(state: AgentState):
    """Create a summary from the prioritized tasks and plan."""
    if not state.tasks:
        state.response = "You have no pending tasks."
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
            f"Your next action should be: {next_action}."
        )

    state.current_step = "Tasks summarized"

    return state


graph = StateGraph(AgentState)

graph.add_node("get_tasks", get_tasks_node)
graph.add_node("prioritize_tasks", prioritize_tasks_node)
graph.add_node("plan_next_action", plan_next_action_node)
graph.add_node("summarize_tasks", summarize_tasks_node)

graph.add_edge(START, "get_tasks")
graph.add_edge("get_tasks", "prioritize_tasks")
graph.add_edge("prioritize_tasks", "plan_next_action")
graph.add_edge("plan_next_action", "summarize_tasks")
graph.add_edge("summarize_tasks", END)

lifeadmin_agent = graph.compile()