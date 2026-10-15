
from dataclasses import dataclass, field


@dataclass
class AgentState:
    user_request: str = ""
    session_id: str = ""
    intent: str = ""
    tasks: list = field(default_factory=list)
    current_step: str = ""
    plan: list = field(default_factory=list)
    approval_required: bool = False
    approved: bool = False
    response: str = ""
