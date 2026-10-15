
from app.agents.approval import approve_action, reject_action
from app.agents.state import AgentState
from app.agents.workflow import lifeadmin_agent


def prepare_request(user_request: str, session_id: str):
    """Prepare a request for the current session."""

    state = AgentState(
        user_request=user_request,
        session_id=session_id,
        approved=False,
    )

    return lifeadmin_agent.invoke(state)


def approve_request(state):
    """Approve the prepared action."""

    agent_state = AgentState(**state)
    return approve_action(agent_state)


def reject_request(state):
    """Reject the prepared action."""

    agent_state = AgentState(**state)
    return reject_action(agent_state)


def execute_approved_request(state):
    """Execute an approved action for its original session."""

    agent_state = AgentState(**state)

    result = lifeadmin_agent.invoke(agent_state)

    return AgentState(**result)
