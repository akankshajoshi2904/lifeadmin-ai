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

print("\nTasks:")
print(result["tasks"])

print("\nAgent Response:")
print(result["response"])