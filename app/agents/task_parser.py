
import re


DATE_PATTERN = (
    r"\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{4}"
)

RELATIVE_DATE_PATTERN = (
    r"(?:today|tomorrow|tonight|"
    r"this evening|this afternoon|this morning|"
    r"next week|next month|this weekend|"
    r"next Monday|next Tuesday|next Wednesday|next Thursday|"
    r"next Friday|next Saturday|next Sunday)"
)


def extract_requested_priority(user_request: str):
    """Extract an explicitly requested priority."""
    request = user_request or ""

    match = re.search(
        r"\b(low|medium|high)\s+priority\b"
        r"|\bpriority\s+(?:to|as|is)\s+(low|medium|high)\b"
        r"|\b(?:make it|mark it|set it to)\s+"
        r"(low|medium|high)\b"
        r"|\b(?:urgent|urgently|asap|as soon as possible)\b",
        request,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    value = next((group for group in match.groups() if group), None)

    if not value:
        return "High"

    value = value.lower()

    if value == "urgent" or value == "urgently" or value in {
        "asap",
        "as soon as possible",
    }:
        return "High"

    return value.title()


def extract_task_title(user_request: str) -> str:
    """Extract the task itself, excluding dates and task-management instructions."""
    request = (user_request or "").strip()

    if not request:
        return ""

    # Explicit quoted task titles take precedence.
    quoted = re.search(r"""["']([^"']+)["']""", request)

    if quoted:
        return quoted.group(1).strip()

    # Keep only the first sentence when later sentences contain
    # separate instructions, e.g. "Set the priority to High."
    request = re.split(
        r"(?<=[.!?])\s+(?=(?:set|change|make|mark|update|"
        r"give|assign|raise|lower)\b)",
        request,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()

    # Remove common request prefixes.
    prefixes = [
        r"^(?:please\s+)?remind me to\s+",
        r"^(?:please\s+)?remind me about\s+",
        r"^(?:please\s+)?create a task called\s+",
        r"^(?:please\s+)?create a task to\s+",
        r"^(?:please\s+)?create a task for\s+",
        r"^(?:please\s+)?create task called\s+",
        r"^(?:please\s+)?add a task called\s+",
        r"^(?:please\s+)?add a task to\s+",
        r"^(?:please\s+)?add a task for\s+",
        r"^(?:please\s+)?make a task called\s+",
        r"^(?:please\s+)?make a task to\s+",
        r"^(?:please\s+)?make a reminder to\s+",
        r"^(?:please\s+)?set a reminder to\s+",
        r"^(?:please\s+)?new task to\s+",
        r"^(?:please\s+)?new task for\s+",
        r"^(?:please\s+)?don't forget to\s+",
        r"^(?:please\s+)?do not forget to\s+",
        r"^(?:please\s+)?remember to\s+",
        r"^(?:please\s+)?i need to\s+",
        r"^(?:please\s+)?i have to\s+",
        r"^(?:please\s+)?i must\s+",
        r"^(?:please\s+)?i should\s+",
        r"^(?:please\s+)?i want to\s+",
    ]

    for prefix in prefixes:
        request = re.sub(
            prefix,
            "",
            request,
            count=1,
            flags=re.IGNORECASE,
        )
        if not request:
            return ""

    # Remove trailing instructions that describe task metadata.
    request = re.sub(
        r"\s+(?:and\s+)?(?:set|change|make|mark|update|give|assign|"
        r"raise|lower)\s+(?:the\s+)?"
        r"(?:priority|deadline|due date)\b.*$",
        "",
        request,
        flags=re.IGNORECASE,
    )

    request = re.sub(
        r"\s+(?:and\s+)?(?:make it|mark it)\s+"
        r"(?:urgent|high priority|medium priority|low priority)\b.*$",
        "",
        request,
        flags=re.IGNORECASE,
    )

    # Remove explicit priority phrases if they appear in the same sentence.
    request = re.sub(
        r"\s+(?:with\s+)?(?:low|medium|high)\s+priority\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    request = re.sub(
        r"\s+(?:as\s+)?(?:urgent|urgently|asap|"
        r"as soon as possible)\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    # Remove explicit calendar dates.
    request = re.sub(
        rf"\s+(?:by|before|on|due on|due by)\s+{DATE_PATTERN}\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    request = re.sub(
        rf"\s+{DATE_PATTERN}\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    # Remove relative dates from the title, while the date parser
    # independently extracts the actual deadline.
    request = re.sub(
        rf"\s+(?:by|before|on|due on|due by)\s+{RELATIVE_DATE_PATTERN}\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    request = re.sub(
        rf"\s+{RELATIVE_DATE_PATTERN}\b",
        "",
        request,
        flags=re.IGNORECASE,
    )

    # Clean up common connecting words left by removing metadata.
    request = re.sub(r"\s+", " ", request).strip()
    request = re.sub(r"^(?:to|for)\s+", "", request, flags=re.IGNORECASE)

    return request.strip(" \t\r\n\"'.,;:!?-")
