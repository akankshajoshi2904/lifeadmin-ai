import re


def analyze_document(text):
    result = {
        "document_type": "Unknown",
        "important_date": None,
        "amount": None,
        "action_required": None,
        "priority": "Low",
    }

    text_lower = text.lower()

    # -----------------------------
    # Detect document type
    # -----------------------------

    if "insurance" in text_lower or "policy" in text_lower:
        result["document_type"] = "Insurance"

    elif "invoice" in text_lower or "payment due" in text_lower:
        result["document_type"] = "Bill / Invoice"

    elif "warranty" in text_lower:
        result["document_type"] = "Warranty"

    elif "rent" in text_lower or "lease" in text_lower:
        result["document_type"] = "Rent / Lease"

    elif "college" in text_lower or "university" in text_lower:
        result["document_type"] = "Education"

    # -----------------------------
    # Find dates
    # -----------------------------

    date_pattern = (
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b"
    )

    dates = re.findall(
        date_pattern,
        text,
        re.IGNORECASE
    )

    if dates:
        result["important_date"] = dates[-1]

    # -----------------------------
    # Find money amounts
    # -----------------------------

    amount_pattern = (
        r"(?:₹|Rs\.?|INR|■)\s?"
        r"[\d,]+(?:\.\d{2})?"
    )

    amounts = re.findall(
        amount_pattern,
        text,
        re.IGNORECASE
    )

    if amounts:
        result["amount"] = amounts[-1]

    # -----------------------------
    # Detect required action
    # -----------------------------

    action_keywords = [
        "renew",
        "pay",
        "submit",
        "apply",
        "register",
        "respond",
        "complete",
    ]

    for keyword in action_keywords:

        if keyword in text_lower:

            result["action_required"] = keyword.capitalize()
            result["priority"] = "High"

            break

    return result