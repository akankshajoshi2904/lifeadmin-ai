
import os

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
    request = user_request.lower()

    if any(
        phrase in request
        for phrase in [
            "create a task",
            "add a task",
            "new task",
            "remind me",
        ]
    ):
        return "create_task"

    if any(
        phrase in request
        for phrase in [
            "complete",
            "finish",
            "done",
            "mark as completed",
        ]
    ):
        return "complete_task"

    if any(
        phrase in request
        for phrase in [
            "upcoming",
            "due soon",
            "next",
        ]
    ):
        return "upcoming_tasks"

    return "review_tasks"


def detect_intent(user_request: str) -> str:
    """Use OpenAI for intent classification, with a rule-based fallback."""
    if not user_request or not user_request.strip():
        return "review_tasks"

    if not os.getenv("OPENAI_API_KEY"):
        return detect_intent_with_rules(user_request)

    try:
        from app.ai_client import ask_ai

        answer = ask_ai(
            "Classify the user's request into exactly one of these "
            "categories: create_task, complete_task, upcoming_tasks, "
            "review_tasks.\n"
            "Return only the category name, with no explanation.\n\n"
            f"User request: {user_request}"
        )

        intent = answer.strip().lower()

        if intent in VALID_INTENTS:
            return intent

    except Exception:
        # Keep the application usable when the API is unavailable.
        pass

    return detect_intent_with_rules(user_request)
