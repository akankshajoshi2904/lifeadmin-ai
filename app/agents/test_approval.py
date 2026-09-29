from app.agents.state import AgentState
from app.agents.approval import approve_action, reject_action


state = AgentState(
    user_request="Create a task to submit my project report.",
    approval_required=True,
    approved=False,
)

print("Before approval:")
print("Approval Required:", state.approval_required)
print("Approved:", state.approved)

approved_state = approve_action(state)

print("\nAfter approval:")
print("Approval Required:", approved_state.approval_required)
print("Approved:", approved_state.approved)
print("Current Step:", approved_state.current_step)

assert approved_state.approved is True
assert approved_state.current_step == "Action approved"

rejected_state = AgentState(
    user_request="Create a task to submit my project report.",
    approval_required=True,
    approved=False,
)

rejected_state = reject_action(rejected_state)

print("\nAfter rejection:")
print("Approval Required:", rejected_state.approval_required)
print("Approved:", rejected_state.approved)
print("Current Step:", rejected_state.current_step)

assert rejected_state.approved is False
assert rejected_state.approval_required is False
assert rejected_state.current_step == "Action rejected"

print("\nAll approval tests passed.")