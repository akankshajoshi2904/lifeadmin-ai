from app.agents.task_parser import extract_task_title


test_cases = [
    (
        "Create a task to submit my project report.",
        "submit my project report",
    ),
    (
        "Add a task for renewing insurance.",
        "renewing insurance",
    ),
    (
        "Remind me to pay the electricity bill.",
        "pay the electricity bill",
    ),
    (
        "Finish my assignment.",
        "Finish my assignment",
    ),
]


for request, expected in test_cases:
    actual = extract_task_title(request)

    print(f"Request: {request}")
    print(f"Expected: {expected}")
    print(f"Extracted: {actual}")

    assert actual == expected

    print("Result: PASS")
    print()