from typing import Any, Dict

from langchain_core.messages import HumanMessage

from apps.agent_runtime.graphs.state import AgentState


def analyze_node(state: AgentState) -> Dict[str, Any]:
    messages = list(state.get("messages",[]))
    if not messages:
        prompt_text = state['input_data'].get("prompt") or str(state["input_data"])
        messages.append(HumanMessage(content = prompt_text))
    return {
        "messages": messages,
        "status": "RUNNING"
    }

def format_node(state: AgentState)-> Dict[str, Any]:
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

