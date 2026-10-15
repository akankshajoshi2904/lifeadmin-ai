
from app.agents.approval import approve_action, reject_action
from app.agents.state import AgentState
from app.tools.task_tools import (
    create_task_tool,
    complete_task_tool,
    reopen_task_tool,
    update_task_tool,
    delete_task_tool,
)


def prepare_request(user_request: str, session_id: str):
    """Prepare a request for the current user's session."""
    state = AgentState(
        user_request=user_request,
        session_id=session_id,
        approved=False,
    )

    from app.agents.workflow import lifeadmin_agent

    return lifeadmin_agent.invoke(state)


def approve_request(state):
    """Approve only an action that was prepared for approval."""
    agent_state = AgentState(**state)

    if not agent_state.approval_required:
        raise ValueError("There is no pending action to approve.")

    if agent_state.clarification_required:
        raise ValueError("Please clarify the request before approving it.")

    if agent_state.intent in {
        "complete_task",
        "reopen_task",
        "update_task",
        "delete_task",
    } and agent_state.selected_task_id is None:
        raise ValueError("No specific task was selected for this action.")

    return approve_action(agent_state)


def reject_request(state):
    """Reject the prepared action without modifying any task."""
    agent_state = AgentState(**state)
    return reject_action(agent_state)


def execute_approved_request(state):
    """Execute the exact approved action without rerunning task selection."""
    agent_state = AgentState(**state)

    if not agent_state.approved or not agent_state.approval_required:
        raise ValueError("The action has not been approved.")

    if agent_state.clarification_required:
        raise ValueError("The request still requires clarification.")

    session_id = agent_state.session_id
    task_id = agent_state.selected_task_id
    changes = agent_state.proposed_changes or {}
    intent = agent_state.intent

    if not session_id:
        raise ValueError("The session ID is missing.")

    if intent == "create_task":
        title = changes.get("title")
        if not title:
            raise ValueError("The task title is missing.")

        created = create_task_tool(
            title=title,
            due_date=changes.get("due_date"),
            priority=changes.get("priority", "Medium"),
            session_id=session_id,
        )

        agent_state.response = (
            f"Task created successfully: {title}."
            if created
            else f"This task already exists: {title}."
        )

    elif intent == "complete_task":
        if task_id is None:
            raise ValueError("The task ID is missing.")

        if not complete_task_tool(task_id, session_id):
            raise ValueError("The task could not be completed.")

        agent_state.response = "Task completed successfully."

    elif intent == "reopen_task":
        if task_id is None:
            raise ValueError("The task ID is missing.")

        if not reopen_task_tool(task_id, session_id):
            raise ValueError("The task could not be reopened.")

        agent_state.response = "Task reopened successfully."

    elif intent == "update_task":
        if task_id is None:
            raise ValueError("The task ID is missing.")

        if not changes:
            raise ValueError("No task changes were provided.")

        # A missing due_date key means leave the date unchanged.
        # A null due_date explicitly clears it.
        if changes.get("clear_due_date"):
            updated = update_task_tool(
                task_id=task_id,
                session_id=session_id,
                title=changes.get("title"),
                priority=changes.get("priority"),
                status=changes.get("status"),
            )

            if updated:
                from app.task_manager import clear_task_due_date

                updated = clear_task_due_date(task_id, session_id)
        else:
            updated = update_task_tool(
                task_id=task_id,
                session_id=session_id,
                title=changes.get("title"),
                due_date=changes.get("due_date"),
                priority=changes.get("priority"),
                status=changes.get("status"),
            )

        if not updated:
            raise ValueError(
                "The task could not be updated. It may no longer exist."
            )

        agent_state.response = "Task updated successfully."

    elif intent == "delete_task":
        if task_id is None:
            raise ValueError("The task ID is missing.")

        if not delete_task_tool(task_id, session_id):
            raise ValueError("The task could not be deleted.")

        agent_state.response = "Task deleted successfully."

    else:
        raise ValueError(f"Unsupported approved action: {intent}")

    agent_state.approval_required = False
    agent_state.approved = False
    agent_state.current_step = "Task executed"

    return agent_state
