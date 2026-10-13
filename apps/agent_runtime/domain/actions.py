from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    FINAL_RESPONSE = "FINAL_RESPONSE"
    CALL_TOOL = "CALL_TOOL"
    CALL_AGENT = "CALL_AGENT"
    CREATE_PLAN = "CREATE_PLAN"
    WAIT = "WAIT"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"

class AgentDecision(BaseModel):
    thought: str = Field(description= "The internal reasoning/thought process leading to the decision")
    action_type: ActionType = Field(description = "The explicit action type the runtime is authorized to execute")
    action_payload : Dict[str, Any] = Field(default_factory=dict, description = "Parameters required for the action (e.g tool name and arguments")
