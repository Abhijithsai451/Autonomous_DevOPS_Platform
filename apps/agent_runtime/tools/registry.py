from typing import Dict, Any, List, Callable, Optional
from langchain_core.tools import BaseTool, StructuredTool
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

class ToolRegistry:
    """
    Centralized registry for managing agent capabilities and dynamic tool resolution.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a BaseTool instance."""
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing registered tool: {tool.name}")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: '{tool.name}'")

    def register_func(
        self,
        func: Callable,
        name: str,
        description: str,
        args_schema: Optional[type] = None,
    ) -> None:
        """Registers a plain Python function as a LangChain StructuredTool."""
        tool = StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema,
        )
        self.register(tool)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def resolve_tools_for_agent(self, enabled_tool_names: List[str]) -> List[BaseTool]:
        """
        Resolves active tools requested by an agent's configuration.
        """
        resolved = []
        for name in enabled_tool_names:
            tool = self.get_tool(name)
            if tool:
                resolved.append(tool)
            else:
                logger.error(f"Requested tool '{name}' not found in registry.")
        return resolved


# Global runtime registry instance
tool_registry = ToolRegistry()