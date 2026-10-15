
from datetime import datetime
import re

from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.router import detect_intent
from app.agents.task_parser import extract_task_title
from app.agents.task_date_parser import extract_due_date
from app.agents.memory import get_memory
from app.tools.task_tools import create_task_tool, complete_task_tool


def detect_intent_node(state: AgentState):
    state.intent = detect_intent(state.user_request)
    state.current_step = "Intent detected"
    return state


def get_tasks_node(state: AgentState):
    state.tasks = get_memory(state.session_id)
    state.current_step = "Tasks retrieved from memory"
    return state


def prioritize_tasks_node(state: AgentState):
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


def find_requested_task(state):
    """Find a specifically named task, or choose the next task if unnamed."""
    pending_tasks = state.tasks

    if not pending_tasks:
        return None

    request = state.user_request.strip()

    match = re.search(
        r"\b(?:task|assignment)\s+(?:named|called)\s+(.+?)[?.!]*$",
        request,
        re.IGNORECASE,
    )

    if match:
        requested_title = match.group(1).strip().strip("\"' ")
        requested_title = re.sub(
            r"[?.!]+$",
            "",
            requested_title,
        ).strip()

        for task in pending_tasks:
            if task["title"].casefold() == requested_title.casefold():
                return task

        return None

    return pending_tasks[0]


def plan_next_action_node(state: AgentState):
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

    if state.intent == "complete_task":
        selected_task = find_requested_task(state)

        if selected_task is None:
            state.plan = []
            state.current_step = "No action available"
            return state

        state.plan = [selected_task["title"]]
        state.current_step = "Plan created"
        return state

    state.plan = [task["title"] for task in state.tasks]
    state.current_step = "Plan created"
    return state


def prepare_execution_node(state: AgentState):
    if state.intent in ["upcoming_tasks", "review_tasks"]:
        state.approval_required = False
        state.current_step = "Information ready"
        return state

    if state.intent == "create_task":
        state.approval_required = True
        state.response = (
            f"Task ready to create: {extract_task_title(state.user_request)}. "
            + (
                f"Due date: {extract_due_date(state.user_request)}. "
                if extract_due_date(state.user_request)
                else ""
            )
            + "Human approval is required before creation."
        )
        state.current_step = "Waiting for approval"
        return state

    if state.intent == "complete_task":
        if not state.plan:
            state.approval_required = False
            state.response = (
                "I couldn't find the requested task in your pending tasks. "
                "No changes were made."
            )
            state.current_step = "No action available"
            return state

        state.approval_required = True
        state.response = (
            f"Ready to complete task: {state.plan[0]}. "
            "Human approval is required before execution."
        )
        state.current_step = "Waiting for approval"
        return state

    state.approval_required = False
    state.current_step = "Information ready"
    return state


def execute_task_node(state: AgentState):
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
            session_id=state.session_id,
        )

        if created:
            state.response = f"Task created successfully: {task_title}."
            if due_date:
                state.response += f" Due date: {due_date}."
        else:
            state.response = f"The task already exists: {task_title}."

        state.approval_required = False
        state.approved = False
        state.current_step = "Task executed"
        return state

    if state.intent == "complete_task":
        if not state.plan:
            state.approval_required = False
            state.approved = False
            state.current_step = "No action available"
            return state

        selected_title = state.plan[0]
        selected_task = next(
            (
                task for task in state.tasks
                if task["title"].casefold() == selected_title.casefold()
            ),
            None,
        )

        if selected_task is None:
            state.approval_required = False
            state.approved = False
            state.response = "The selected task was not found. No changes were made."
            state.current_step = "No action available"
            return state

        updated = complete_task_tool(
            selected_task["id"],
            session_id=state.session_id,
        )

        if not updated:
            state.approval_required = False
            state.approved = False
            state.response = "The selected task was not found. No changes were made."
            state.current_step = "No action available"
            return state

        state.response = (
            f"Task completed successfully: {selected_task['title']}."
        )
        state.approval_required = False
        state.approved = False
        state.current_step = "Task executed"
        return state

    state.current_step = "No action available"
    return state


def summarize_tasks_node(state: AgentState):
    if state.intent == "create_task":
        if state.current_step == "Execution blocked":
            task_title = extract_task_title(state.user_request)
            due_date = extract_due_date(state.user_request)

            state.response = f"Task ready to create: {task_title}. "
            if due_date:
                state.response += f"Due date: {due_date}. "

            state.response += "Human approval is required before creation."

        return state

    if state.intent == "complete_task":
        if state.current_step == "Execution blocked" and state.plan:
            state.response = (
                f"Ready to complete task: {state.plan[0]}. "
                "Human approval is required before execution."
            )
        return state

    if not state.tasks:
        state.response = "You have no pending tasks."
        state.current_step = "Tasks summarized"
        return state

    if state.intent == "upcoming_tasks":
        upcoming_tasks = [
            task for task in state.tasks
            if task["urgency"] in ["Upcoming", "Due Soon", "Overdue"]
        ]

        if upcoming_tasks:
            task_lines = [
                f"{task['title']} — Due: {task['due_date']} ({task['urgency']})"
                for task in upcoming_tasks
            ]
            state.response = (
                "Here are your upcoming tasks:\n" + "\n".join(task_lines)
            )
        else:
            state.response = "You have no upcoming tasks."

    else:
        due_soon = [
            task for task in state.tasks
            if task["urgency"] in ["Overdue", "Due Soon"]
        ]
        high_priority = [
            task for task in state.tasks
            if task["priority"] == "High"
        ]
        next_action = state.plan[0] if state.plan else "Review your tasks"

        state.response = (
            f"You have {len(state.tasks)} pending task(s). "
            f"{len(high_priority)} are high priority. "
            f"{len(due_soon)} need attention within the next 7 days. "
            f"Your next action should be: {next_action}."
        )

    state.current_step = "Tasks summarized"
    return state


def route_by_intent(state: AgentState):
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
