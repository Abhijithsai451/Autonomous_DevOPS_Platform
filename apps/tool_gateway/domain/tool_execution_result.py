from enum import Enum
from typing import Optional, Any, Dict

from pydantic import BaseModel, Field


class ToolExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"


class ToolExecutionResult(BaseModel):
    execution_id: str
    status: ToolExecutionStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    duration_ms: int