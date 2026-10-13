from typing import List, Annotated, Any, Dict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict

from apps.agent_runtime.application.runtime.context import ExecutionContext


class AgentGraphState(TypedDict):
    context: ExecutionContext
    messages: Annotated[List[BaseMessage], add_messages]

    iteration_count : int
    max_iterations : int
    is_finished : bool
    final_output: Dict[str, Any]

    
