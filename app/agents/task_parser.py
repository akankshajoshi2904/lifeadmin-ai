def extract_task_title(user_request: str) -> str:
    """Extract a clean task title from a natural-language request."""

    request = user_request.strip()

    prefixes = [
        "create a task to ",
        "create a task for ",
        "add a task to ",
        "add a task for ",
        "new task to ",
        "new task for ",
        "remind me to ",
        "remind me about ",
    ]

    request_lower = request.lower()

    for prefix in prefixes:
        if request_lower.startswith(prefix):
            title = request[len(prefix):].strip()
            return title.rstrip(".!?")

    return request.rstrip(".!?")