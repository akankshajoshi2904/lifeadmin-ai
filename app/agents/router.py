def detect_intent(user_request: str) -> str:
    """Detect the user's requested action using simple rules."""

    request = user_request.lower()

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
            "upcoming",
            "due soon",
            "next",
        ]
    ):
        return "upcoming_tasks"

    return "review_tasks"