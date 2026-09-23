from app.agents.state import AgentState
from app.agents.workflow import lifeadmin_agent


state = AgentState(
    user_request="Complete my next task.",
    approved=False
)

result = lifeadmin_agent.invoke(state)

print("User Request:")
print(result["user_request"])

print("\nIntent:")
print(result["intent"])

print("\nCurrent Step:")
print(result["current_step"])

print("\nApproval Required:")
print(result["approval_required"])

print("Approved:")
print(result["approved"])

print("\nPlan:")
for step_number, action in enumerate(result["plan"], start=1):
    print(f"{step_number}. {action}")

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