from typing import Any, Dict

from apps.tool_gateway.domain.tool_execution_request import ToolExecutionRequest
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger

class AuthorizationEngine:
    """
    Evaluates permissions for tool execution (supports local policies and OPA integration).
    """
    async def is_authorized(self, request: ToolExecutionRequest) -> bool:
        if not request.organization_id:
            logger.warning("Denied tool execution: Missing organization_id scope.")
            return False

        if not request.agent_id:
            logger.warning("Denied tool execution: Missing agent_id identifier.")
            return False

        if request.tool_slug == "http_request":
            method = str(request.input_data.get("method", "")).upper()
            if method in ["DELETE"] and request.organization_id != "admin_org":
                logger.warning(f"Denied HTTP DELETE operation for org {request.organization_id}")
                return False

        return True

auth_engine = AuthorizationEngine()