from typing import Dict, Any

from apps.tool_gateway.domain.tool_definition import ToolDefinition, ToolStatus
from apps.tool_gateway.tools.base import BaseTool


class EchoTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            id="tool_echo_v1",
            name="Echo Tool",
            slug="echo",
            description="Returns the provided input payload intact.",
            version="1.0.0",
            status=ToolStatus.ACTIVE,
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"echo": input_data.get("message")}