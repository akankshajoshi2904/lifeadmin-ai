from app.agents.approval import approve_action, reject_action
from app.agents.state import AgentState
from app.agents.workflow import lifeadmin_agent


def prepare_request(user_request: str):
    """Run the agent until it reaches a human approval decision."""

    state = AgentState(
        user_request=user_request,
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