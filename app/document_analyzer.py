
import re
from datetime import datetime


def analyze_document(text):
    result = {
        "document_type": "Unknown",
        "important_date": None,
        "amount": None,
        "action_required": None,
        "priority": "Low",
    }

    text_lower = text.lower()

    # Detect document type
    if "insurance" in text_lower or "policy" in text_lower:
        result["document_type"] = "Insurance"
    elif (
        "invoice" in text_lower
        or "payment due" in text_lower
        or "bill" in text_lower
    ):
        result["document_type"] = "Bill / Invoice"
    elif "warranty" in text_lower:
        result["document_type"] = "Warranty"
    elif "rent" in text_lower or "lease" in text_lower:
        result["document_type"] = "Rent / Lease"
    elif any(
        word in text_lower
        for word in ["college", "university", "assignment", "project report"]
    ):
        result["document_type"] = "Education"

    # Find the earliest upcoming date and its sentence
    date_pattern = (
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b"
    )

    today = datetime.now().date()
    upcoming = []

    for match in re.finditer(date_pattern, text, re.IGNORECASE):
        try:
            parsed_date = datetime.strptime(
                match.group(), "%d %B %Y"
            ).date()
        except ValueError:
            continue

        if parsed_date >= today:
            # Find the sentence containing this date.
            start = text.rfind(".", 0, match.start()) + 1
            end = text.find(".", match.end())
            if end == -1:
                end = len(text)

            sentence = text[start:end].strip()
            upcoming.append((parsed_date, match.group(), sentence))

    if upcoming:
        upcoming.sort(key=lambda item: item[0])
        earliest_date, date_text, sentence = upcoming[0]

        result["important_date"] = date_text
        sentence_lower = sentence.lower()

        # Detect the action in the earliest-deadline sentence.
        action_patterns = [
            (r"\bsubmit(?:s|ted|ting)?\b", "Submit"),
            (r"\bpay(?:s|ment|ing|paid)?\b", "Pay"),
            (r"\brenew(?:s|al|ed|ing)?\b", "Renew"),
            (r"\battend(?:s|ed|ing)?\b", "Attend"),
            (r"\bprepare(?:s|d|ing)?\b", "Prepare"),
            (r"\breview(?:s|ed|ing)?\b", "Review"),
            (r"\bemail(?:s|ed|ing)?\b", "Email"),
            (r"\bapply\b", "Apply"),
            (r"\bregister\b", "Register"),
            (r"\brespond\b", "Respond"),
            (r"\bcomplete\b", "Complete"),
        ]

        for pattern, action in action_patterns:
            if re.search(pattern, sentence_lower):
                result["action_required"] = action
                break

        # Estimate priority from the relevant sentence.
        if any(
            keyword in sentence_lower
            for keyword in ["urgent", "immediately", "overdue", "final deadline"]
        ):
            result["priority"] = "High"
        elif result["action_required"]:
            result["priority"] = "Medium"

    # Find the first money amount
    amount_pattern = r"(?:₹|Rs\.?|INR|■)\s?[\d,]+(?:\.\d{2})?"
    amounts = re.findall(amount_pattern, text, re.IGNORECASE)

    if amounts:
        result["amount"] = amounts[0]

    # If there are no dated actions, detect an action from the full document.
    if result["action_required"] is None:
        fallback_patterns = [
            (r"\bsubmit\b", "Submit"),
            (r"\bpay\b", "Pay"),
            (r"\brenew\b", "Renew"),
            (r"\battend\b", "Attend"),
            (r"\bprepare\b", "Prepare"),
            (r"\breview\b", "Review"),
            (r"\bemail\b", "Email"),
            (r"\bapply\b", "Apply"),
            (r"\bregister\b", "Register"),
            (r"\brespond\b", "Respond"),
            (r"\bcomplete\b", "Complete"),
        ]

        for pattern, action in fallback_patterns:
            if re.search(pattern, text_lower):
                result["action_required"] = action
                result["priority"] = "Medium"
                break

    return result
