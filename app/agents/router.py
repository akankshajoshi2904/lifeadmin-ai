
import os
import re

from dotenv import load_dotenv

load_dotenv()

VALID_INTENTS = {
    "create_task",
    "complete_task",
    "upcoming_tasks",
    "review_tasks",
}


def detect_intent_with_rules(user_request: str) -> str:
    """Detect intent using local rules without an API call."""
    request = user_request.lower().strip()

    if not request:
        return "review_tasks"

    # Detect task completion requests in different wordings.
    completion_patterns = [
        r"\bmark\b.+\bas\s+(?:completed|complete|done)\b",
        r"\bmark\b.+\b(?:completed|complete|done)\s*[.!?]*$",
        r"\bcomplete\s+(?:the\s+)?task\b",
        r"\bfinish\s+(?:the\s+)?task\b",
        r"\btask\s+is\s+done\b",
        r"\bmark\s+task\s+as\s+done\b",
    ]

    if any(
        re.search(pattern, request)
        for pattern in completion_patterns
    ):
        return "complete_task"

    # Detect adding an item to a to-do list before review rules.
    if re.search(
        r"\b(add|put|include)\b.+\bto my (to-do|todo) list\b",
        request,
    ):
        return "create_task"

    # Explicit and natural task-creation requests.
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

    # Common actions expressed with a deadline.
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

    # Trust clear rule-based matches without requiring an API call.
    if rule_intent != "review_tasks":
        return rule_intent

    if not os.getenv("OPENAI_API_KEY"):
        return rule_intent

    try:
        from app.ai_client import ask_ai

        answer = ask_ai(
            "Classify the user's request into exactly one category: "
            "create_task, complete_task, upcoming_tasks, review_tasks.\n"
            "Use create_task when the user wants to create a task or "
            "expresses an obligation.\n"
            "Use complete_task when the user asks to mark an existing "
            "task as completed or done, or asks to finish a task.\n"
            "Use review_tasks when the user asks to see existing tasks.\n"
            "Use upcoming_tasks when the user asks about upcoming deadlines.\n"
            "Return only the category name.\n\n"
            f"User request: {user_request}"
        )

        intent = answer.strip().lower()

        if intent in VALID_INTENTS:
            return intent

    except Exception:
        pass

    return rule_intent
