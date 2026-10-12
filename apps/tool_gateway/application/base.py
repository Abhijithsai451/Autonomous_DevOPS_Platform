from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, Dict, Any

from pydantic import BaseModel


class ToolRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class BaseTool(ABC):
    name : str
    description: str
    version: str = "1.0.0"
    risk_level : ToolRiskLevel = ToolRiskLevel.LOW
    timeout_seconds: float = 30.0

    args_schema = Type[BaseModel]

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any])-> Dict[str, Any]:
        """
        Execute the tool logic with the validated arguemnts
        """
        pass

