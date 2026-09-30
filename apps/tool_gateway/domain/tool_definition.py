from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field


class ToolStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"

class ToolDefinition(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    version: str = "1.0.0"
    status: ToolStatus = ToolStatus.ACTIVE
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)