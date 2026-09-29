import re


def extract_due_date(user_request: str):
    """Extract a due date written as day month year."""

    pattern = (
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b"
    )

    match = re.search(
        pattern,
        user_request,
        re.IGNORECASE
    )

    if match:
        return match.group(0)

    return None