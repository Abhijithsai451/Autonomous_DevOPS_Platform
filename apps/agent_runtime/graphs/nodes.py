from typing import Any, Dict

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import interrupt

from apps.agent_runtime.graphs.state import AgentState
from apps.agent_runtime.llm.factory import get_llm_model
from apps.agent_runtime.tools.system_tool import DEFAULT_TOOLS, TOOLS_BY_NAME


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
    llm_with_tools = llm.bind_tools[DEFAULT_TOOLS]

    response = llm_with_tools.invoke(state['messages'])
    updated_messages = list(state["messages"]) + [response]

    return {"messages": updated_messages}

def tool_node(state: AgentState)-> Dict[str, Any]:
    """
    Executes tool calls requested in the latest AI Message
    """
    messages = list(state["messages"])
    last_message = messages[-1]

    tool_results = list(state.get("tool_results", []))

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            selected_tool = TOOLS_BY_NAME.get(tool_name)
            if selected_tool:
                try:
                    result = selected_tool.invoke(tool_args)
                    tool_output = str(result)
                except Exception as e:
                    tool_output = f"Error executing {tool_name}: {str(e)}"
            else:
                tool_output = f"Tool {tool_name} not found"

            tool_results.append(
                {
                    "tool": tool_name,
                    "args": tool_args,
                    "output": tool_output,
                }
            )

            messages.append(
                ToolMessage(content = tool_output, tool_call_id = tool_call_id)
            )
        return {"messages": messages, "tool_results": tool_results}

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

