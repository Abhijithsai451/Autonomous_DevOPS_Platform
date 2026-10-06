from typing import Any, Dict

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from apps.agent_runtime.graphs.state import AgentState
from apps.agent_runtime.llm.factory import get_llm_model


def analyze_node(state: AgentState) -> Dict[str, Any]:
    """
    Pauses the graph Execution and wait for the Human Approval
    """
    tool_calls = []
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        tool_calls = messages[-1].tool_calls

    approval_decision = interrupt({
        "reason": "HUMAN_APPROVAL_REQUIRED",
        "pending_tool_calls": tool_calls,
        "run_id": state.get("run_id"),
    })

    if not approval_decision.get("approved", False):
        return {
            "status": "CANCELLED",
            "error": {"code": "APPROVAL_REJECTED", "message": approval_decision.get("reason", "Rejected by operator")}
        }

    return {"status": "RUNNING"}

def llm_node(state: AgentState)-> Dict[str, Any]:
    """
    Invokes the LLM model with the tools bound
    """
    llm = get_llm_model()

    response = llm.invoke(state['messages'])
    updated_messages = list(state["messages"]) + [response]

    return {"messages": updated_messages}

def format_node(state: AgentState)-> Dict[str, Any]:
    """
    Formats the final output for AgentRuns
    """
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    output_text = last_message.content if last_message else ""

    return {
        "output_data": {
            "result": output_text,
            "raw_messages": [m.dict() for m in messages]
        },
        "status": "COMPLETED"
    }

