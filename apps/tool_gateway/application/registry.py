from typing import Dict, Optional

from apps.tool_gateway.domain.tool_definition import ToolStatus
from apps.tool_gateway.tools.base import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.definition.slug] = tool

    def get_tool(self, slug: str) -> Optional[BaseTool]:
        tool = self._tools.get(slug)
        if tool and tool.definition.status == ToolStatus.ACTIVE:
            return tool
        return None


tool_registry = ToolRegistry()