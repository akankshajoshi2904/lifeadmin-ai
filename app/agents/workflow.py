
import re
from datetime import datetime

from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.router import detect_intent
from app.agents.task_parser import (
    extract_task_title,
    extract_requested_priority,
)
from app.agents.task_date_parser import extract_due_date
from app.agents.memory import get_memory


ACTION_INTENTS = {
    "create_task",
    "complete_task",
    "reopen_task",
    "update_task",
    "delete_task",
}


def detect_intent_node(state: AgentState):
    state.intent = detect_intent(state.user_request)
    state.current_step = "Intent detected"
    return state


def get_tasks_node(state: AgentState):
    state.tasks = get_memory(state.session_id)
    state.current_step = "Tasks retrieved"
    return state


def prioritize_tasks_node(state: AgentState):
    """Add urgency information without removing completed tasks."""
    today = datetime.now().date()
    prioritized = []

    for original_task in state.tasks:
        task = dict(original_task)
        due_date = task.get("due_date")

        try:
            due = datetime.strptime(due_date, "%d %B %Y").date()
            days_left = (due - today).days
        except (ValueError, TypeError):
            days_left = None

        if task.get("status") != "Pending":
            urgency = "Completed"
        elif days_left is None:
            urgency = "No deadline"
        elif days_left < 0:
            urgency = "Overdue"
        elif days_left <= 7:
            urgency = "Due Soon"
        elif days_left <= 30:
            urgency = "Upcoming"
        else:
            urgency = "Later"

        task["days_left"] = days_left
        task["urgency"] = urgency
        prioritized.append(task)

    prioritized.sort(
        key=lambda task: (
            task["status"] != "Pending",
            task["days_left"] is None,
            task["days_left"]
            if task["days_left"] is not None
            else 999999,
            task["priority"] != "High",
        )
    )

    state.tasks = prioritized
    state.current_step = "Tasks prioritized"
    return state


def _extract_target_title(state: AgentState) -> str:
    """Extract the target task from common action requests."""
    request = state.user_request.strip()

    patterns = [
        # Change the priority of my gym task to Low.
        r"^(?:please\s+)?(?:change|set|update|edit|modify)\s+"
        r"(?:the\s+)?priority\s+(?:of\s+)?(.+?)\s+"
        r"(?:to|as|is)\s+(?:low|medium|high)"
        r"(?:\s+priority)?[.!]?$",

        # Change my gym task priority to Low.
        r"^(?:please\s+)?(?:change|set|update|edit|modify)\s+"
        r"(.+?)\s+priority\s+(?:to|as|is)\s+"
        r"(?:low|medium|high)(?:\s+priority)?[.!]?$",

        # Change the deadline of my gym task to 20 October 2026.
        r"^(?:please\s+)?(?:change|set|update|edit|modify)\s+"
        r"(?:the\s+)?(?:deadline|due date)\s+(?:of|for)\s+"
        r"(.+?)\s+(?:to|as)\s+\d{1,2}\s+"
        r"[A-Za-z]+\s+\d{4}[.!]?$",

        r"^(?:please\s+)?(?:change|set|update|edit|modify)\s+"
        r"(.+?)\s+(?:deadline|due date)\s+(?:to|as)\s+"
        r"\d{1,2}\s+[A-Za-z]+\s+\d{4}[.!]?$",

        r"^(?:please\s+)?rename\s+(.+?)\s+to\s+.+[.!]?$",
        r"^(?:please\s+)?change\s+(?:the\s+)?title\s+of\s+"
        r"(.+?)\s+to\s+.+[.!]?$",

        # Complete, reopen, or delete a named task.
        r"^(?:please\s+)?(?:complete|finish|reopen|delete|remove)"
        r"\s+(?:the\s+)?(.+?)[.!]?$",
        r"^(?:please\s+)?mark\s+(.+?)\s+as\s+"
        r"(?:completed|complete|done|pending)[.!]?$",
    ]

    for pattern in patterns:
        match = re.match(pattern, request, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip("\"' ")

    named = re.search(
        r"\b(?:task|assignment|reminder)\s+"
        r"(?:named|called)\s+(.+?)[.!]?$",
        request,
        re.IGNORECASE,
    )

    if named:
        return named.group(1).strip().strip("\"' ")

    return extract_task_title(request)


def _extract_update_changes(state: AgentState) -> dict:
    """Extract only changes explicitly requested by the user."""
    request = state.user_request.strip()
    changes = {}

    priority = extract_requested_priority(request)
    if priority:
        changes["priority"] = priority

    due_date = extract_due_date(request)
    if due_date:
        changes["due_date"] = due_date

    rename_patterns = [
        r"^(?:please\s+)?rename\s+.+?\s+to\s+(.+?)[.!]?$",
        r"^(?:please\s+)?change\s+(?:the\s+)?title\s+of\s+"
        r".+?\s+to\s+(.+?)[.!]?$",
    ]

    for pattern in rename_patterns:
        match = re.match(pattern, request, re.IGNORECASE)
        if match:
            changes["title"] = match.group(1).strip().strip("\"' ")
            break

    return changes


def _normalize_title(title: str) -> str:
    """Normalize a title for case-insensitive natural-language matching."""
    title = str(title or "").casefold()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def _find_requested_task(state: AgentState):
    """
    Find a task using exact or unique meaningful-word matches.

    For updates, prefer a unique Pending task over completed tasks.
    Never automatically choose between multiple plausible tasks.
    """
    raw_target = _extract_target_title(state).strip()

    if not raw_target:
        return None, []

    target = _normalize_title(raw_target)

    generic_words = {
        "my", "the", "a", "an", "task", "tasks",
        "reminder", "reminders", "todo", "todos",
        "assignment", "assignments", "please",
    }

    target_words = {
        word for word in target.split()
        if word not in generic_words
    }

    if not target_words:
        return None, []

    if state.intent == "complete_task":
        eligible = [
            task for task in state.tasks
            if task.get("status") == "Pending"
        ]

    elif state.intent == "reopen_task":
        eligible = [
            task for task in state.tasks
            if task.get("status") == "Completed"
        ]

    elif state.intent == "update_task":
        # First look for a match among active tasks.
        pending_tasks = [
            task for task in state.tasks
            if task.get("status") == "Pending"
        ]
        eligible = pending_tasks if pending_tasks else list(state.tasks)

    else:
        # Preserve existing matching behavior for delete and other actions.
        eligible = list(state.tasks)

    normalized_titles = {
        id(task): _normalize_title(task.get("title", ""))
        for task in eligible
    }

    # Exact title match.
    exact_matches = [
        task for task in eligible
        if normalized_titles[id(task)] == target
    ]

    if len(exact_matches) == 1:
        return exact_matches[0], []

    if len(exact_matches) > 1:
        return None, exact_matches

    # Match when all meaningful reference words occur in the title.
    all_word_matches = [
        task for task in eligible
        if target_words.issubset(
            set(normalized_titles[id(task)].split())
        )
    ]

    if len(all_word_matches) == 1:
        return all_word_matches[0], []

    if len(all_word_matches) > 1:
        return None, all_word_matches

    # Suggest likely candidates for clarification; never guess.
    partial_matches = [
        task for task in eligible
        if target in normalized_titles[id(task)]
        or normalized_titles[id(task)] in target
        or target_words.intersection(
            set(normalized_titles[id(task)].split())
        )
    ]

    return None, partial_matches


def plan_next_action_node(state: AgentState):
    state.plan = []
    state.selected_task_id = None
    state.selected_task = {}
    state.proposed_changes = {}
    state.clarification_required = False
    state.approval_required = False

    if state.intent == "create_task":
        title = extract_task_title(state.user_request)
        due_date = extract_due_date(state.user_request)
        priority = extract_requested_priority(state.user_request) or "Medium"

        if not title:
            state.clarification_required = True
            state.current_step = "Clarification required"
            state.response = "What task would you like me to create?"
            return state

        state.proposed_changes = {
            "title": title,
            "due_date": due_date,
            "priority": priority,
        }

        state.plan = [
            f"Create task: {title}",
            f"Priority: {priority}",
        ]

        if due_date:
            state.plan.append(f"Due date: {due_date}")

        state.current_step = "Plan created"
        return state

    if state.intent in {
        "complete_task",
        "reopen_task",
        "update_task",
        "delete_task",
    }:
        selected, suggestions = _find_requested_task(state)

        if selected is None:
            state.clarification_required = True
            state.current_step = "Clarification required"

            if suggestions:
                choices = "\n".join(
                    f"- {task['title']} (ID {task['id']}, "
                    f"{task.get('status', 'Unknown')})"
                    for task in suggestions[:5]
                )
                state.response = (
                    "I couldn't identify one exact task. "
                    "Which task did you mean?\n" + choices
                )
            else:
                state.response = (
                    "I couldn't find a matching task. "
                    "Please describe the task or provide its title "
                    "as shown in My Tasks. No changes were made."
                )

            return state

        state.selected_task_id = selected["id"]
        state.selected_task = dict(selected)

        if state.intent == "complete_task":
            state.plan = [f"Complete: {selected['title']}"]

        elif state.intent == "reopen_task":
            state.plan = [f"Reopen: {selected['title']}"]

        elif state.intent == "delete_task":
            state.plan = [
                f"Delete: {selected['title']}",
                "This action permanently removes the task.",
            ]

        elif state.intent == "update_task":
            changes = _extract_update_changes(state)

            if not changes:
                state.clarification_required = True
                state.current_step = "Clarification required"
                state.response = (
                    f"What would you like to change about "
                    f"'{selected['title']}'? You can change its title, "
                    "deadline, or priority."
                )
                state.selected_task_id = None
                state.selected_task = {}
                return state

            state.proposed_changes = changes
            state.plan = [f"Update: {selected['title']}"]

            for field, new_value in changes.items():
                old_value = selected.get(field)
                if old_value is None or old_value == "":
                    old_value = "Not set"

                state.plan.append(
                    f"{field.replace('_', ' ').title()}: "
                    f"{old_value} → {new_value}"
                )

        state.current_step = "Plan created"
        return state

    state.current_step = "Plan created"
    return state


def prepare_execution_node(state: AgentState):
    """Prepare mutations for approval; never approve them automatically."""
    if state.clarification_required:
        state.approval_required = False
        return state

    if state.intent in {"review_tasks", "upcoming_tasks"}:
        state.approval_required = False
        state.current_step = "Information ready"
        return state

    if state.intent in ACTION_INTENTS:
        if state.intent != "create_task" and state.selected_task_id is None:
            state.approval_required = False
            state.current_step = "No action available"
            return state

        state.approval_required = True
        state.approved = False
        state.current_step = "Waiting for approval"

        if state.intent == "create_task":
            state.response = (
                "Please review the proposed task. Nothing will be saved "
                "until you approve it."
            )
        else:
            state.response = (
                "Please review the selected task and proposed action. "
                "Nothing will change until you approve it."
            )

        return state

    state.approval_required = False
    state.current_step = "Information ready"
    return state


def execute_task_node(state: AgentState):
    """Preparation never executes a database mutation."""
    if state.intent in ACTION_INTENTS and state.approval_required:
        state.current_step = "Waiting for approval"
    else:
        state.current_step = "Information only"

    return state


def summarize_tasks_node(state: AgentState):
    if state.clarification_required:
        return state

    if state.intent in ACTION_INTENTS:
        return state

    pending = [
        task for task in state.tasks
        if task.get("status") == "Pending"
    ]

    if state.intent == "upcoming_tasks":
        upcoming = [
            task for task in pending
            if task.get("urgency") in {"Overdue", "Due Soon", "Upcoming"}
        ]

        if not upcoming:
            state.response = "You have no upcoming tasks."
        else:
            lines = [
                f"- {task['title']} — Due: "
                f"{task.get('due_date') or 'Not set'} "
                f"({task.get('urgency', 'Unknown')})"
                for task in upcoming
            ]
            state.response = (
                "Here are your upcoming tasks:\n" + "\n".join(lines)
            )

    else:
        if not pending:
            state.response = "You have no pending tasks."
        else:
            high_priority = sum(
                task.get("priority") == "High" for task in pending
            )
            due_soon = sum(
                task.get("urgency") in {"Overdue", "Due Soon"}
                for task in pending
            )

            lines = [
                f"- {task['title']} | "
                f"Due: {task.get('due_date') or 'Not set'} | "
                f"Priority: {task.get('priority') or 'Medium'}"
                for task in pending
            ]

            state.response = (
                f"You have {len(pending)} pending task(s), "
                f"{high_priority} high-priority task(s), and "
                f"{due_soon} overdue or near-deadline task(s).\n\n"
                + "\n".join(lines)
            )

    state.current_step = "Tasks summarized"
    return state


def route_by_intent(state: AgentState):
    return "get_tasks"


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
    {"get_tasks": "get_tasks"},
)
graph.add_edge("get_tasks", "prioritize_tasks")
graph.add_edge("prioritize_tasks", "plan_next_action")
graph.add_edge("plan_next_action", "prepare_execution")
graph.add_edge("prepare_execution", "execute_task")
graph.add_edge("execute_task", "summarize_tasks")
graph.add_edge("summarize_tasks", END)

lifeadmin_agent = graph.compile()
