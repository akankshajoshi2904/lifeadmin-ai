
import re


DATE_PATTERN = (
    r"\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{4}"
)


def extract_task_title(user_request: str) -> str:
    """Extract a task title from common task-related requests."""
    request = user_request.strip()

    if not request:
        return ""

    # Prefer an explicitly quoted title.
    quoted = re.search(r"""["']([^"']+)["']""", request)
    if quoted:
        return quoted.group(1).strip()

    patterns = [
        r"^mark\s+(.+?)\s+as\s+(?:completed|complete|done|pending)[.!]?$",
        r"^mark\s+(.+?)\s+(?:completed|complete|done)[.!]?$",
        r"^(?:complete|finish|reopen|delete|remove)\s+"
        r"(?:the\s+)?(?:task\s+)?(.+?)(?:\s+task)?[.!]?$",
        r"^(?:update|edit|change|modify|rename|reschedule)\s+"
        r"(?:the\s+)?(?:task\s+)?(.+?)[.!]?$",
        r"^(?:task|assignment)\s+(?:named|called)\s+(.+?)[.!]?$",
    ]

    for pattern in patterns:
        match = re.match(pattern, request, flags=re.IGNORECASE)
        if match:
            title = match.group(1).strip().strip("\"' ")
            title = re.sub(
                r"\s+priority\s+(?:to|as|is)\s+(?:low|medium|high)$",
                "",
                title,
                flags=re.IGNORECASE,
            )
            title = re.sub(
                r"\s+(?:to|for)\s+(?:low|medium|high)\s+priority$",
                "",
                title,
                flags=re.IGNORECASE,
            )
            return title.rstrip(".!?").strip()

    # Creation prefixes
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

    for prefix in prefixes:
        if request.lower().startswith(prefix):
            request = request[len(prefix):].strip()
            break

    request = re.sub(
        rf"\s+(?:by|before|on)\s+{DATE_PATTERN}\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    return request.strip().strip("\"'").rstrip(".!?")


def extract_requested_priority(user_request: str):
    """Extract an explicitly requested priority, if present."""
    match = re.search(
        r"\b(low|medium|high)\s+priority\b"
        r"|\bpriority\s+(?:to|as|is)\s+(low|medium|high)\b",
        user_request,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return next(group for group in match.groups() if group).title()
