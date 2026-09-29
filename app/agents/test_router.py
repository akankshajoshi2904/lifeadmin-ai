from app.agents.router import detect_intent


test_cases = [
    ("Complete my assignment", "complete_task"),
    ("Show my upcoming tasks", "upcoming_tasks"),
    ("Create a task to renew insurance", "create_task"),
    ("What should I do?", "review_tasks"),
]


for request, expected_intent in test_cases:
    actual_intent = detect_intent(request)

    print(f"Request: {request}")
    print(f"Expected: {expected_intent}")
    print(f"Detected: {actual_intent}")

    assert actual_intent == expected_intent

    print("Result: PASS")
    print()