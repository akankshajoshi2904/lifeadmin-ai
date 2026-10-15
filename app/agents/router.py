
import os
import re

from dotenv import load_dotenv

load_dotenv()

VALID_INTENTS = {
    "create_task",
    "complete_task",
    "reopen_task",
    "update_task",
    "delete_task",
    "upcoming_tasks",
    "review_tasks",
}


def detect_intent_with_rules(user_request: str) -> str:
    """Detect common task intents using local rules."""
    request = user_request.lower().strip()

    if not request:
        return "review_tasks"

    # Deleting must be checked before creation or review.
    if re.search(
        r"\b(delete|remove|erase|discard)\b.*\b(task|reminder|todo|to-do)\b"
        r"|\b(delete|remove|erase)\s+(?:it|that|this|the duplicate)\b",
        request,
    ):
        return "delete_task"

    # Reopening a completed task.
    if re.search(
        r"\b(reopen|uncomplete|undo completion|mark .+ as pending)\b",
        request,
    ) or (
        re.search(r"\b(mark|set)\b", request)
        and re.search(r"\b(pending|not done|incomplete)\b", request)
    ):
        return "reopen_task"

    # Updating task details.
    update_patterns = [
        r"\b(update|edit|change|modify|rename|reschedule)\b",
        r"\b(move|push|shift)\b.+\b(deadline|due date|date)\b",
        r"\b(set|make)\b.+\b(priority|deadline|due date)\b",
        r"\b(change|correct|fix)\b.+\b(task|deadline|priority|title)\b",
    ]

    if any(re.search(pattern, request) for pattern in update_patterns):
        return "update_task"

    # Completing a task.
    completion_patterns = [
        r"\bmark\b.+\bas\s+(?:completed|complete|done)\b",
        r"\bmark\b.+\b(?:completed|complete|done)\s*[.!?]*$",
        r"\bcomplete\s+(?:the\s+)?task\b",
        r"\bfinish\s+(?:the\s+)?task\b",
        r"\btask\s+is\s+done\b",
        r"\bmark\s+task\s+as\s+done\b",
        r"\b(i have|i've|i just)\s+(?:finished|completed|done)\b",
    ]

    if any(re.search(pattern, request) for pattern in completion_patterns):
        return "complete_task"

    # Adding items to a to-do list.
    if re.search(
        r"\b(add|put|include)\b.+\bto my (to-do|todo) list\b",
        request,
    ):
        return "create_task"

    # Explicit task-creation requests.
    if any(
        phrase in request
        for phrase in [
            "create a task",
            "create task",
            "add a task",
            "add task",
            "new task",
            "make a task",
            "make a reminder",
            "set a reminder",
            "remind me",
            "schedule a task",
            "i need to",
            "i have to",
            "i must",
            "i should",
            "don't forget to",
            "need to remember to",
            "remember to",
        ]
    ):
        return "create_task"

    # Upcoming tasks and deadlines.
    if any(
        phrase in request
        for phrase in [
            "upcoming tasks",
            "what is due",
            "what's due",
            "due soon",
            "tasks due",
            "deadlines coming up",
            "what do i need to do next",
        ]
    ):
        return "upcoming_tasks"

    # Review existing tasks.
    if any(
        phrase in request
        for phrase in [
            "show my tasks",
            "list my tasks",
            "review my tasks",
            "review tasks",
            "what are my tasks",
            "what tasks do i have",
            "how many tasks",
            "show tasks",
            "list tasks",
            "my to-do list",
            "my todo list",
        ]
    ):
        return "review_tasks"

    # A deadline plus an action often means a new task.
    has_deadline = re.search(
        r"\b(by|before|on|tomorrow|tonight|today|next week|"
        r"next month|this weekend)\b",
        request,
    )

    action_verbs = {
        "pay", "submit", "finish", "complete", "attend",
        "buy", "send", "prepare", "visit", "go", "call",
        "email", "study", "renew", "book", "upload",
        "register", "apply", "meet", "do", "file",
    }

    if has_deadline and action_verbs.intersection(request.split()):
        return "create_task"

    return "review_tasks"


def detect_intent(user_request: str) -> str:
    """Classify requests using rules and AI when available."""
    if not user_request or not user_request.strip():
        return "review_tasks"

    rule_intent = detect_intent_with_rules(user_request)

    # Use AI for requests that are not clearly classified by the rules.
    if rule_intent != "review_tasks":
        return rule_intent

    if not os.getenv("OPENAI_API_KEY"):
        return rule_intent

    try:
        from app.ai_client import ask_ai

        answer = ask_ai(
            "Classify the user's request into exactly one category: "
            "create_task, complete_task, reopen_task, update_task, "
            "delete_task, upcoming_tasks, review_tasks.\n"
            "Use create_task for creating a new task.\n"
            "Use complete_task for completing an existing task.\n"
            "Use reopen_task for reopening a completed task.\n"
            "Use update_task for changing existing task details.\n"
            "Use delete_task for deleting an existing task.\n"
            "Use upcoming_tasks for upcoming deadlines.\n"
            "Use review_tasks for viewing or reviewing tasks.\n"
            "Return only the category name.\n\n"
            f"User request: {user_request}"
        )

        intent = answer.strip().lower()

        if intent in VALID_INTENTS:
            return intent

    except Exception:
        pass

    return rule_intent
