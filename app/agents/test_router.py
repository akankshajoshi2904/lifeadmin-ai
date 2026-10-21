
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
    """Identify the requested task action, prioritizing clear intent."""
    request = re.sub(r"\s+", " ", (user_request or "").strip().lower())

    if not request:
        return "review_tasks"

    # Explicit creation/reminder language takes priority over task details.
    creation_starts = (
        "remind me to ",
        "remind me about ",
        "create a task ",
        "create task ",
        "add a task ",
        "add task ",
        "make a task ",
        "make a reminder ",
        "set a reminder ",
        "new task ",
        "don't forget to ",
        "do not forget to ",
        "remember to ",
        "need to remember to ",
    )

    if request.startswith(creation_starts):
        return "create_task"

    # Explicit additions to a to-do list.
    if re.search(
        r"\b(?:add|put|include)\b.+\bto my (?:to-do|todo) list\b",
        request,
    ):
        return "create_task"

    # Delete/remove requests, including conversational wording.
    if re.search(
        r"\b(?:delete|remove|erase|discard)\b",
        request,
    ) and re.search(
        r"\b(?:task|reminder|todo|to-do|it|that|this|one|duplicate)\b",
        request,
    ):
        return "delete_task"

    if re.search(
        r"\b(?:i don't need|i do not need|no longer need)\b.+"
        r"\b(?:task|reminder|it|that)\b",
        request,
    ):
        return "delete_task"

    # Reopening completed tasks.
    if re.search(
        r"\b(?:reopen|uncomplete|undo completion)\b",
        request,
    ) or re.search(
        r"\b(?:mark|set)\b.+\b(?:pending|not done|incomplete)\b",
        request,
    ):
        return "reopen_task"

    # Completing existing tasks.
    if re.search(
        r"\b(?:mark|set)\b.+\b(?:as\s+)?(?:completed|complete|done)\b",
        request,
    ) or re.search(
        r"\b(?:complete|finish|check off)\b.+"
        r"\b(?:task|assignment|todo|to-do)\b",
        request,
    ) or re.search(
        r"\b(?:task|assignment)\b.+\b(?:is done|is finished|is complete)\b",
        request,
    ) or re.search(
        r"\b(?:i have|i've|i just)\s+(?:finished|completed)\b",
        request,
    ):
        return "complete_task"

    # Explicit modifications to an existing task.
    update_patterns = [
        r"\b(?:update|edit|modify|rename|reschedule)\b",
        r"\bchange\b.+\b(?:priority|deadline|due date|title)\b",
        r"\b(?:raise|lower|increase|decrease)\b.+\bpriority\b",
        r"\b(?:move|push|shift|postpone|bring forward)\b.+"
        r"\b(?:deadline|due date|task)\b",
        r"\bset\b.+\bpriority\b",
        r"\bmake\b.+\bpriority\b",
        r"\bchange\b.+\bpriority\b",
    ]

    if any(re.search(pattern, request) for pattern in update_patterns):
        return "update_task"

    # Generic task creation language.
    if re.search(
        r"\b(?:i need to|i have to|i must|i should|i want to)\b",
        request,
    ):
        return "create_task"

    if re.search(
        r"\b(?:please|can you|could you)\s+"
        r"(?:add|create|make|schedule|remember)\b",
        request,
    ):
        return "create_task"

    # Queries about upcoming deadlines.
    if any(
        phrase in request
        for phrase in (
            "upcoming tasks",
            "what is due",
            "what's due",
            "what is coming up",
            "what's coming up",
            "due soon",
            "tasks due",
            "deadlines coming up",
            "what do i need to do next",
        )
    ):
        return "upcoming_tasks"

    # Requests to view existing tasks.
    if any(
        phrase in request
        for phrase in (
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
        )
    ):
        return "review_tasks"

    # A deadline plus an actionable activity often means task creation.
    has_deadline = re.search(
        r"\b(?:by|before|on|tomorrow|tonight|today|"
        r"next week|next month|this weekend)\b",
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
    """Use deterministic rules first and AI for ambiguous requests."""
    if not user_request or not user_request.strip():
        return "review_tasks"

    rule_intent = detect_intent_with_rules(user_request)

    # Clear action rules should not be overridden by an AI guess.
    if rule_intent != "review_tasks":
        return rule_intent

    if not os.getenv("OPENAI_API_KEY"):
        return rule_intent

    try:
        from app.ai_client import ask_ai

        answer = ask_ai(
            "Classify this request into exactly one category: "
            "create_task, complete_task, reopen_task, update_task, "
            "delete_task, upcoming_tasks, review_tasks.\n"
            "Create means adding a NEW task or reminder.\n"
            "Update means changing an EXISTING task.\n"
            "Complete means marking an existing task done.\n"
            "Reopen means making a completed task pending again.\n"
            "Delete means removing an existing task.\n"
            "Upcoming means asking about future deadlines.\n"
            "Review means viewing or summarizing existing tasks.\n"
            "If a request starts by asking to be reminded to do "
            "something, classify it as create_task, even if it also "
            "mentions a priority or deadline.\n"
            "Return only the category name.\n\n"
            f"User request: {user_request}"
        )

        intent = answer.strip().lower()

        if intent in VALID_INTENTS:
            return intent

    except Exception:
        pass

    return rule_intent
