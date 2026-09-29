from app.agents.task_date_parser import extract_due_date


test_cases = [
    (
        "Create a task to submit my report by 5 October 2026.",
        "5 October 2026",
    ),
    (
        "Remind me to pay the bill on 12 November 2026.",
        "12 November 2026",
    ),
    (
        "Create a task to prepare for my exam.",
        None,
    ),
]


for request, expected in test_cases:
    actual = extract_due_date(request)

    print(f"Request: {request}")
    print(f"Expected: {expected}")
    print(f"Extracted: {actual}")

    assert actual == expected

    print("Result: PASS")
    print()