from typing import Dict, Type, List

from apps.tool_gateway.application.base import BaseTool
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_class: Type[BaseTool])-> Type[BaseTool]:
        """
        Decorator or method to register a tool instance
        """
        tool_instance = tool_class()
        if tool_instance.name in self._tools:
            logger.warning(f"Tool: '{tool_instance}' is already registerd. Overwriting. ")

        self._tool[tool_instance.name] = tool_instance
        logger.info(f"Registered Tool: {tool_instance.name} (Risk: {tool_instance.risk_level.value}")
        return tool_class

    def get(self, name: str)-> BaseTool:
        tool = self._tools.get(name)
        if not tool:
            raise KeyError(f"No tool with name {tool} found in the registry")
        return tool

    def list_tools(self)-> List[BaseTool]:
        tools = list(self._tools.values())
        return tools

tool_regsitry = ToolRegistry()