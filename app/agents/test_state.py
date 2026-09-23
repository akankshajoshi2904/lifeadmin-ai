from app.agents.state import AgentState


state = AgentState(
    user_request="What do I need to take care of?",
    current_step="Planning tasks"
)

state.tasks = [
    {
        "title": "Renew Insurance",
        "due_date": "14 October 2026",
        "priority": "High"
    }
]

state.plan = [
    "Renew Insurance"
]

state.response = "Your next action is to renew your insurance."


print("User Request:", state.user_request)
print("Current Step:", state.current_step)
print("Tasks:", state.tasks)
print("Plan:", state.plan)
print("Response:", state.response)