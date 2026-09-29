from app.agents.controller import (
    prepare_request,
    approve_request,
    reject_request,
)


state = prepare_request(
    "Create a task to review the LifeAdmin project by 20 October 2026."
)

print("Prepared request:")
print("Intent:", state["intent"])
print("Approval Required:", state["approval_required"])
print("Approved:", state["approved"])
print("Plan:", state["plan"])
print("Response:", state["response"])

assert state["approval_required"] is True
assert state["approved"] is False

print("\nApproval decision:")

approved_state = approve_request(state)

print("Approved:", approved_state.approved)
print("Current Step:", approved_state.current_step)

assert approved_state.approved is True

print("\nController approval test passed.")