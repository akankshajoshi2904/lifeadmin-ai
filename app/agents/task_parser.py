
import re


DATE_PATTERN = (
    r"\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s*\d{4}"
)

RELATIVE_DATE_PATTERN = (
    r"(?:day after tomorrow|today|tomorrow|tonight|"
    r"this evening|this afternoon|this morning|"
    r"next week|next month|this weekend|"
    r"next Monday|next Tuesday|next Wednesday|next Thursday|"
    r"next Friday|next Saturday|next Sunday)"
)


def extract_requested_priority(user_request: str):
    """Extract an explicitly requested priority."""
    request = user_request or ""

    patterns = [
        r"\bpriority\s+(?:to|as|is)\s+(low|medium|high)\b",
        r"\b(low|medium|high)\s+priority\b",
        r"\b(?:set|change|make|mark|update|lower|raise|"
        r"increase|decrease)\b.{0,100}?\bto\s+(low|medium|high)\b",
        r"\b(?:make it|mark it|set it to)\s+(low|medium|high)\b",
        r"\b(urgent|urgently|asap|as soon as possible)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, request, flags=re.IGNORECASE)
        if not match:
            continue

        value = next(
            (group for group in match.groups() if group),
            None,
        )

        if not value:
            continue

        value = value.lower()

        if value in {
            "urgent",
            "urgently",
            "asap",
            "as soon as possible",
        }:
            return "High"

        return value.title()

    return None


def extract_task_title(user_request: str) -> str:
    """Extract the task title, excluding dates and metadata instructions."""
    request = (user_request or "").strip()

    if not request:
        return ""

    # Explicit quoted titles take precedence.
    quoted = re.search(r"""["']([^"']+)["']""", request)
    if quoted:
        return quoted.group(1).strip()

    # Ignore a later sentence that only supplies metadata.
    request = re.split(
        r"(?<=[.!?])\s+(?=(?:set|change|make|mark|update|"
        r"give|assign|raise|lower|increase|decrease)\b)",
        request,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()

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

    # Remove trailing metadata instructions.
    request = re.sub(
        r"\s+(?:and\s+)?(?:set|change|make|mark|update|give|"
        r"assign|raise|lower|increase|decrease)\s+"
        r"(?:the\s+)?(?:priority|deadline|due date)\b.*$",
        "",
        request,
        flags=re.IGNORECASE,
    )

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

    request = re.sub(
        rf"\s+(?:by|before|on|due on|due by)\s+"
        rf"{RELATIVE_DATE_PATTERN}\b",
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

    request = re.sub(r"\s+", " ", request).strip()

    request = re.sub(
        r"^(?:to|for)\s+",
        "",
        request,
        flags=re.IGNORECASE,
    )

    return request.strip(" \t\r\n\"'.,;:!?-")


if __name__ == "__main__":
    examples = [
        "Create a task to submit my project report by 5 October2026.",
        "Create a task called Test LifeAdmin with high priority",
    ]

    for example in examples:
        print("Request:", example)
        print("Title:", extract_task_title(example))
        print("Priority:", extract_requested_priority(example))
        print()
