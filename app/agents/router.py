
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
    """Detect task-management intents using explicit language rules."""
    request = (user_request or "").lower().strip()

    if not request:
        return "review_tasks"

    # Explicit creation requests take priority.
    explicit_creation_patterns = [
        r"\bcreate\b.{0,40}\btask\b",
        r"\badd\b.{0,40}\btask\b",
        r"\bnew task\b",
        r"\bmake a task\b",
        r"\bmake a reminder\b",
        r"\bset a reminder\b",
        r"\bschedule a task\b",
        r"\bremind me to\b",
        r"\bremind me about\b",
        r"\bdon't forget to\b",
        r"\bdo not forget to\b",
        r"\badd\b.+\bto my (?:to-do|todo) list\b",
        r"\bput\b.+\bto my (?:to-do|todo) list\b",
    ]

    if any(re.search(pattern, request) for pattern in explicit_creation_patterns):
        return "create_task"

    # Delete an existing task.
    if re.search(
        r"\b(delete|remove|erase|discard)\b.*"
        r"\b(task|reminder|todo|to-do|assignment)\b"
        r"|\b(delete|remove|erase)\s+"
        r"(?:it|that|this|the duplicate)\b",
        request,
    ):
        return "delete_task"

    # Reopen a completed task.
    if (
        re.search(
            r"\b(reopen|uncomplete|undo completion)\b",
            request,
        )
        or re.search(
            r"\bmark\b.+\bas\s+(?:pending|incomplete|not done)\b",
            request,
        )
        or re.search(
            r"\b(set|mark)\b.+\b(?:pending|incomplete|not done)\b",
            request,
        )
    ):
        return "reopen_task"

    # Complete or finish an existing task.
    completion_patterns = [
        r"\bcomplete\b.+\b(task|assignment|reminder)\b",
        r"\bfinish\b.+\b(task|assignment|reminder)\b",
        r"\bmark\b.+\bas\s+(?:completed|complete|done)\b",
        r"\bmark\b.+\b(?:completed|complete|done)\s*[.!?]*$",
        r"\btask\s+is\s+done\b",
        r"\bmark\s+task\s+as\s+done\b",
        r"\b(i have|i've|i just)\s+(?:finished|completed)\b",
    ]

    if any(re.search(pattern, request) for pattern in completion_patterns):
        return "complete_task"

    # Update an existing task.
    update_patterns = [
        r"\b(update|edit|change|modify|rename|reschedule)\b",
        r"\b(move|push|shift)\b.+\b(deadline|due date|date)\b",
        r"\b(set|make)\b.+\b(priority|deadline|due date)\b",
        r"\b(change|correct|fix)\b.+\b(task|deadline|priority|title)\b",
    ]

    if any(re.search(pattern, request) for pattern in update_patterns):
        return "update_task"

    # Upcoming deadlines.
    upcoming_phrases = [
        "upcoming tasks",
        "what is due",
        "what's due",
        "due soon",
        "tasks due",
        "deadlines coming up",
        "what do i need to do next",
    ]

    if any(phrase in request for phrase in upcoming_phrases):
        return "upcoming_tasks"

    # View existing tasks.
    review_phrases = [
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

    if any(phrase in request for phrase in review_phrases):
        return "review_tasks"

    # Generic reminders and commitments, when no existing-task action matched.
    generic_creation_patterns = [
        r"\bremember to\b",
        r"\bi need to\b",
        r"\bi have to\b",
        r"\bi must\b",
        r"\bi should\b",
    ]

    if any(
        re.search(pattern, request)
        for pattern in generic_creation_patterns
    ):
        return "create_task"

    # Natural-language requests with a deadline and an action.
    has_deadline = re.search(
        r"\b(today|tomorrow|tonight|next week|next month|"
        r"this weekend|by|before|on)\b",
        request,
    )

    action_verbs = {
        "pay", "submit", "finish", "complete", "attend",
        "buy", "send", "prepare", "visit", "go", "call",
        "email", "study", "renew", "book", "upload",
        "register", "apply", "meet", "do", "file",
    }

    words = set(re.findall(r"[a-z']+", request))

    if has_deadline and action_verbs.intersection(words):
        return "create_task"

    return "review_tasks"


def detect_intent(user_request: str) -> str:
    """Classify a request using rules, with optional AI fallback."""
    if not user_request or not user_request.strip():
        return "review_tasks"

    rule_intent = detect_intent_with_rules(user_request)

    # Explicit rules are deterministic and do not need an AI call.
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
            "Creating a new task or reminder is create_task.\n"
            "Changing an existing task is update_task.\n"
            "Completing an existing task is complete_task.\n"
            "Reopening a completed task is reopen_task.\n"
            "Deleting an existing task is delete_task.\n"
            "Viewing upcoming deadlines is upcoming_tasks.\n"
            "Viewing existing tasks is review_tasks.\n"
            "Return only the category name.\n\n"
            f"User request: {user_request}"
        )

        intent = answer.strip().lower()

        if intent in VALID_INTENTS:
            return intent

    except Exception:
        pass

    return rule_intent
