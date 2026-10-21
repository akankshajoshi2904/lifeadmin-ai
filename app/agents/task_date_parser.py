
import re
from datetime import date, datetime, timedelta


MONTH_PATTERN = (
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December"
)


def _format_date(value: date) -> str:
    """Format dates without a leading zero on the day."""
    return f"{value.day} {value.strftime('%B %Y')}"


def extract_due_date(user_request: str):
    """Extract explicit dates and common relative dates."""
    if not user_request or not user_request.strip():
        return None

    request = user_request.strip()
    lower_request = request.lower()
    today = date.today()

    if re.search(r"\bday after tomorrow\b", lower_request):
        return _format_date(today + timedelta(days=2))

    if re.search(r"\btomorrow\b", lower_request):
        return _format_date(today + timedelta(days=1))

    if re.search(r"\btoday\b", lower_request):
        return _format_date(today)

    if re.search(r"\bnext week\b", lower_request):
        return _format_date(today + timedelta(days=7))

    days_match = re.search(r"\bin\s+(\d+)\s+days?\b", lower_request)
    if days_match:
        return _format_date(
            today + timedelta(days=int(days_match.group(1)))
        )

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
            return _format_date(today + timedelta(days=days_ahead + 7))

        if re.search(rf"\b{ name }\b", lower_request):
            days_ahead = (weekday - today.weekday()) % 7
            days_ahead = days_ahead or 7
            return _format_date(today + timedelta(days=days_ahead))

    pattern = rf"\b\d{{1,2}}\s+(?:{MONTH_PATTERN})\s+\d{{4}}\b"
    match = re.search(pattern, request, re.IGNORECASE)

    if match:
        try:
            parsed = datetime.strptime(match.group(0), "%d %B %Y")
            return _format_date(parsed.date())
        except ValueError:
            return None

    return None
