
import re


def extract_task_title(user_request: str) -> str:
    """Extract a clean task title from a natural-language request."""

    request = user_request.strip()
    if not request:
        return ""

    request_lower = request.lower()

    # Remove completion wording to identify the existing task's title.
    completion_patterns = [
        r"^mark\s+(.+?)\s+as\s+completed[.!]?$",
        r"^mark\s+(.+?)\s+completed[.!]?$",
        r"^mark\s+(.+?)\s+as\s+done[.!]?$",
        r"^complete\s+(?:the\s+)?task\s+(.+?)[.!]?$",
        r"^complete\s+(.+?)[.!]?$",
        r"^finish\s+(?:the\s+)?task\s+(.+?)[.!]?$",
        r"^finish\s+(.+?)[.!]?$",
    ]

    for pattern in completion_patterns:
        match = re.match(pattern, request, flags=re.IGNORECASE)
        if match:
            title = match.group(1).strip().strip("\"'")
            return title.rstrip(".!?")

    # Remove common task-creation prefixes.
    prefixes = [
        "create a task called ",
        "create a task to ",
        "create a task for ",
        "create task called ",
        "add a task called ",
        "add a task to ",
        "add a task for ",
        "add ",
        "new task to ",
        "new task for ",
        "remind me to ",
        "remind me about ",
        "make a task called ",
        "make a task to ",
    ]

    title = request

    for prefix in prefixes:
        if request_lower.startswith(prefix):
            title = request[len(prefix):].strip()
            break

    # Remove quotation marks around the title, if present.
    title = title.strip().strip("\"'")

    # Remove a due-date phrase such as "by 25 October 2026".
    date_pattern = (
        r"\s+(?:by|before|on)\s+"
        r"\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}"
    )

    title = re.sub(
        date_pattern,
        "",
        title,
        flags=re.IGNORECASE,
    )

    return title.strip().rstrip(".!?")
