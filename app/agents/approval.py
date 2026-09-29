def approve_action(state):
    """Approve the action prepared by the agent."""

    if not state.approval_required:
        return state

    state.approved = True
    state.current_step = "Action approved"

    return state


def reject_action(state):
    """Reject the action prepared by the agent."""

    state.approved = False
    state.approval_required = False
    state.current_step = "Action rejected"

    return state