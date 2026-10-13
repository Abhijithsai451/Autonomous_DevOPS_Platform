from typing import List, Dict, Any

from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from fastmcp import Client

class ToolServiceMCPClient:
    def __init__(self, tool_service_url: str):
        self.tool_service_url = tool_service_url
        self.client = Client(tool_service_url)

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Discovers available tools from the remote MCP server.
        Normalizes the output into a clean dictionary list for the Reasoner.
        """
        async with self.client:
            tools_response = await self.client.list_tools()
            normalized_tools = []
            for tool in tools_response:
                normalized_tools.append({
                    "name": getattr(tool, "name", str(tool)),
                    "description": getattr(tool, "description", ""),
                    "input_schema": getattr(tool, "inputSchema", {})
                })

            logger.info(f"Discovered {len(normalized_tools)} tools from MCP Tool Service.")
            return normalized_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Executes a remote tool call via the MCP protocol.
        """
        async with self.client:
            result = await self.client.call_tool(tool_name, arguments)
            return result.content[0].text if result.content else "No output returned."


