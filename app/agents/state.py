from dataclasses import dataclass, field


@dataclass
class AgentState:
    user_request: str = ""
    tasks: list = field(default_factory=list)
    current_step: str = ""
    plan: list = field(default_factory=list)
    response: str = ""