import httpx
from typing import Any, Dict

from apps.tool_gateway.domain.tool_definition import ToolDefinition, ToolStatus
from apps.tool_gateway.tools.base import BaseTool


class HttpRequestTool(BaseTool):
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            id="tool_http_request_v1",
            name="HTTP Request",
            slug="http_request",
            description="Executes controlled outbound HTTP calls.",
            version="1.0.0",
            status=ToolStatus.ACTIVE,
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                    "headers": {"type": "object"},
                    "body": {"type": "object"}
                },
                "required": ["url", "method"]
            }
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        url = input_data["url"]
        method = input_data["method"]
        headers = input_data.get("headers", {})
        body = input_data.get("body")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method=method, url=url, headers=headers, json=body)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if "application/json" in response.headers.get("content-type", "") else response.text
            }