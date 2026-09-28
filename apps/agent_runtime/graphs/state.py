from typing import TypedDict, Any, Dict, Optional, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    run_id : str
    task_id: str
    agent_id: str
    workflow_instance_id: str

    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]

    messages: List[BaseMessage]
    tool_results: List[Dict[str,Any]]

    status: str

