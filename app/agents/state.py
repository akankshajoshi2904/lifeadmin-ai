
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    user_request: str = ""
    session_id: str = ""
    intent: str = ""
    tasks: list = field(default_factory=list)
    current_step: str = ""
    plan: list = field(default_factory=list)

    # Exact task selected for the requested action.
    selected_task_id: int | None = None
    selected_task: dict = field(default_factory=dict)

    # Only the fields the user wants to change.
    proposed_changes: dict = field(default_factory=dict)

    # Approval workflow.
    approval_required: bool = False
    approved: bool = False

    # Used when clarification is needed.
    clarification_required: bool = False

    response: str = ""
