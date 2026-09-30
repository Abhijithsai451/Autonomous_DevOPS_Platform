from typing import Any, Dict

from apps.tool_gateway.domain.tool_definition import ToolDefinition, ToolStatus
from apps.tool_gateway.tools.base import BaseTool


class JsonTransformTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            id="tool_json_transform_v1",
            name="JSON Transform",
            slug="json_transform",
            description="Filters JSON fields based on target key list.",
            version="1.0.0",
            status=ToolStatus.ACTIVE,
            input_schema={
                "type": "object",
                "properties": {
                    "payload": {"type": "object"},
                    "keys": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["payload", "keys"]
            }
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = input_data.get("payload", {})
        keys = input_data.get("keys", [])
        return {"result": {k: payload[k] for k in keys if k in payload}}