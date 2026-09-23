from state import AgentState


state = AgentState(
    user_request="What do I need to take care of?",
    current_step="Reviewing tasks"
)

state.tasks = [
    {
        "title": "Renew Insurance",
        "due_date": "14 October 2026",
        "priority": "High"
    }
]

state.response = "You have one high-priority task."

print("User Request:", state.user_request)
print("Current Step:", state.current_step)
print("Tasks:", state.tasks)
print("Response:", state.response)