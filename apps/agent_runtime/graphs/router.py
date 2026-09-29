from typing import Literal

from langchain_core.messages import AIMessage

from apps.agent_runtime.graphs.state import AgentState


def should_continue(state: AgentState)-> Literal["tools", "format"]:
    """
    Conditional edge router checking for the tools execution requests.
    """
    messages = state.get("messages", [])
    if not messages:
        return "format"

    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "format"