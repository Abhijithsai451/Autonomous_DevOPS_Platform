import httpx
from typing import Any, Dict, Optional

from apps.tool_gateway.config.setttings import tool_gateway_settings as settings
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger


class ComposioAdapter:
    """
    Adapter to discovery, normalize, and execute tools hosted via Composio.
    The Agent Runtime remains agnostic and only calls tool_slugs like 'github.create_issue'.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "COMPOSIO_API_KEY", "")
        self.base_url = "https://backend.composio.dev/api/v1"

    async def execute_action(
        self,
        action_name: str,
        input_data: Dict[str, Any],
        connected_account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("COMPOSIO_API_KEY is not configured on Tool Gateway.")

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "action": action_name,
            "params": input_data
        }
        if connected_account_id:
            payload["connectedAccountId"] = connected_account_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/actions/execute",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                logger.error(f"Composio execution failed: {response.text}")
                return {
                    "success": False,
                    "error": response.json().get("message", "Composio API error"),
                    "raw_response": response.text
                }

            res_data = response.json()
            return {
                "success": res_data.get("successful", True),
                "data": res_data.get("data", {}),
                "error": res_data.get("error")
            }

composio_adapter = ComposioAdapter()