import re


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

    title = request

    for prefix in prefixes:
        if request_lower.startswith(prefix):
            title = request[len(prefix):].strip()
            break

    # Remove a due-date phrase such as:
    # "by 5 October 2026"
    # "on 12 November 2026"
    date_pattern = (
        r"\s+(?:by|on)\s+"
        r"\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}"
    )

    title = re.sub(
        date_pattern,
        "",
        title,
        flags=re.IGNORECASE
    )

    return title.strip().rstrip(".!?")