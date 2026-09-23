from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.tools.task_tools import list_tasks_tool


def get_tasks_node(state: AgentState):
    """Retrieve the user's tasks."""

    tasks = list_tasks_tool()

    state.tasks = tasks
    state.current_step = "Tasks retrieved"

    return state


def summarize_tasks_node(state: AgentState):
    """Create a simple summary from the tasks."""

    if not state.tasks:

        state.response = "You have no tasks."

    else:

        pending_tasks = [
            task
            for task in state.tasks
            if task[4] == "Pending"
        ]

        if not pending_tasks:

            state.response = "You have no pending tasks."

        else:

            high_priority = [
                task
                for task in pending_tasks
                if task[3] == "High"
            ]

            state.response = (
                f"You have {len(pending_tasks)} pending task(s). "
                f"{len(high_priority)} are high priority."
            )

    state.current_step = "Tasks summarized"

    return state


# Create the graph
graph = StateGraph(AgentState)


# Add workflow nodes
graph.add_node(
    "get_tasks",
    get_tasks_node
)

graph.add_node(
    "summarize_tasks",
    summarize_tasks_node
)


# Define workflow
graph.add_edge(
    START,
    "get_tasks"
)

graph.add_edge(
    "get_tasks",
    "summarize_tasks"
)

graph.add_edge(
    "summarize_tasks",
    END
)


# Compile the agent
lifeadmin_agent = graph.compile()