from app.agents.state import AgentState
from app.agents.workflow import lifeadmin_agent


state = AgentState(
    user_request="What do I need to take care of?"
)


result = lifeadmin_agent.invoke(state)


print("User Request:")
print(result["user_request"])

print("\nCurrent Step:")
print(result["current_step"])

print("\nPrioritized Tasks:")

for task in result["tasks"]:

    print(
        f"- {task['title']} | "
        f"Due: {task['due_date']} | "
        f"Priority: {task['priority']} | "
        f"Urgency: {task['urgency']}"
    )


print("\nAgent Response:")
print(result["response"])