from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolExecutionRequest(BaseModel):
    execution_id: str
    agent_run_id: Optional[str] = None
    agent_id: Optional[str] = None
    organization_id: Optional[str] = None
    user_id: Optional[str] = None
    tool_slug: str
    tool_version: Optional[str] = "1.0.0"
    input_data: Dict[str, Any] = Field(default_factory=dict)
    connected_account_id: Optional[str] = None
    timeout_seconds: int = 30