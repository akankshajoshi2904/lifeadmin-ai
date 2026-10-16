
import re
from datetime import date, datetime, timedelta


def extract_due_date(user_request: str):
    """Extract explicit dates and common relative dates."""
    if not user_request:
        return None

    request = user_request.strip()
    lower_request = request.lower()
    today = date.today()

    # Relative dates.
    if re.search(r"\bday after tomorrow\b", lower_request):
        return (today + timedelta(days=2)).strftime("%d %B %Y")

    if re.search(r"\btomorrow\b", lower_request):
        return (today + timedelta(days=1)).strftime("%d %B %Y")

    if re.search(r"\btoday\b", lower_request):
        return today.strftime("%d %B %Y")

    if re.search(r"\bnext week\b", lower_request):
        return (today + timedelta(days=7)).strftime("%d %B %Y")

    if re.search(r"\bin\s+(\d+)\s+days?\b", lower_request):
        match = re.search(r"\bin\s+(\d+)\s+days?\b", lower_request)
        days = int(match.group(1))
        return (today + timedelta(days=days)).strftime("%d %B %Y")

    # Named weekdays: the next occurrence, or next week's occurrence
    # when the user explicitly says "next <weekday>".
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for name, weekday in weekdays.items():
        if re.search(rf"\bnext\s+{name}\b", lower_request):
            days_ahead = (weekday - today.weekday()) % 7
            days_ahead = days_ahead or 7
            return (today + timedelta(days=days_ahead + 7)).strftime(
                "%d %B %Y"
            )

        if re.search(rf"\b{ name }\b", lower_request):
            days_ahead = (weekday - today.weekday()) % 7
            days_ahead = days_ahead or 7
            return (today + timedelta(days=days_ahead)).strftime(
                "%d %B %Y"
            )

    # Explicit dates such as "16 October 2026".
    pattern = (
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b"
    )

    match = re.search(pattern, request, re.IGNORECASE)

    if match:
        try:
            parsed = datetime.strptime(match.group(0), "%d %B %Y")
            return parsed.strftime("%d %B %Y")
        except ValueError:
            return None

    return None
