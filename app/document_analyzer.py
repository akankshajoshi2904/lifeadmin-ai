
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

    # Detect document type using more specific phrases first.
    if any(
        phrase in text_lower
        for phrase in [
            "project report",
            "project submission",
            "assignment",
            "coursework",
            "college",
            "university",
            "academic",
            "student",
        ]
    ):
        result["document_type"] = "Education"
    elif any(
        phrase in text_lower
        for phrase in [
            "rental agreement",
            "rent agreement",
            "lease agreement",
            "tenancy agreement",
            "landlord",
            "tenant",
        ]
    ):
        result["document_type"] = "Rent / Lease"
    elif any(
        phrase in text_lower
        for phrase in ["insurance policy", "insurance premium", "insured person"]
    ):
        result["document_type"] = "Insurance"
    elif any(
        phrase in text_lower
        for phrase in [
            "invoice",
            "payment due",
            "amount payable",
            "utility bill",
            "electricity bill",
        ]
    ):
        result["document_type"] = "Bill / Invoice"
    elif "warranty" in text_lower:
        result["document_type"] = "Warranty"
    elif "insurance" in text_lower:
        result["document_type"] = "Insurance"
    elif "rent" in text_lower or "lease" in text_lower:
        result["document_type"] = "Rent / Lease"
    elif "bill" in text_lower or "invoice" in text_lower:
        result["document_type"] = "Bill / Invoice"

    # Find upcoming dates and the sentence containing each date.
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
            start = max(
                text.rfind(".", 0, match.start()),
                text.rfind("\n", 0, match.start()),
            ) + 1

            possible_ends = [
                position
                for position in [
                    text.find(".", match.end()),
                    text.find("\n", match.end()),
                ]
                if position != -1
            ]

            end = min(possible_ends) if possible_ends else len(text)
            sentence = text[start:end].strip()

            upcoming.append(
                (parsed_date, match.group(), sentence)
            )

    action_patterns = [
        (r"\bsubmit(?:s|ted|ting)?\b", "Submit"),
        (r"\bpay(?:s|ment|ing|paid)?\b", "Pay"),
        (r"\brenew(?:s|al|ed|ing)?\b", "Renew"),
        (r"\battend(?:s|ed|ing)?\b", "Attend"),
        (r"\bprepare(?:s|d|ing)?\b", "Prepare"),
        (r"\breview(?:s|ed|ing)?\b", "Review"),
        (r"\bemail(?:s|ed|ing)?\b", "Email"),
        (r"\bapply(?:s|ied|ing)?\b", "Apply"),
        (r"\bregister(?:s|ed|ing)?\b", "Register"),
        (r"\brespond(?:s|ed|ing)?\b", "Respond"),
        (r"\bcomplete(?:s|d|ing)?\b", "Complete"),
    ]

    if upcoming:
        upcoming.sort(key=lambda item: item[0])
        _, date_text, sentence = upcoming[0]

        result["important_date"] = date_text
        sentence_lower = sentence.lower()

        # Keep the complete relevant sentence as the action.
        for pattern, action in action_patterns:
            if re.search(pattern, sentence_lower):
                cleaned_sentence = re.sub(
                    r"\s+", " ", sentence
                ).strip(" .;:-")

                result["action_required"] = cleaned_sentence
                break

        if any(
            keyword in sentence_lower
            for keyword in [
                "urgent",
                "immediately",
                "overdue",
                "final deadline",
                "high priority",
            ]
        ):
            result["priority"] = "High"
        elif result["action_required"]:
            result["priority"] = "Medium"

    # Detect a money amount, including common Indian currency formats.
    amount_pattern = (
        r"(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d{2})?"
    )
    amounts = re.findall(amount_pattern, text, re.IGNORECASE)

    if amounts:
        result["amount"] = amounts[0]

    # If no upcoming dated action was found, look for an action sentence.
    if result["action_required"] is None:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            for pattern, action in action_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    result["action_required"] = line.strip(" .;:-")
                    result["priority"] = "Medium"
                    break

            if result["action_required"]:
                break

    return result
