from fastapi import APIRouter

from apps.tool_gateway.application.executor import ToolExecutionEngine
from apps.tool_gateway.application.registry import tool_registry
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger
from apps.tool_gateway.domain.tool_execution_request import ToolExecutionRequest
from apps.tool_gateway.domain.tool_execution_result import ToolExecutionResult

router = APIRouter(tags=["tools"])

execution_engine = ToolExecutionEngine(tool_registry)

@router.post("/execute", response_model=ToolExecutionResult)
async def execute_tool(request: ToolExecutionRequest):
    """
    Standardized execution boundary endpoint called by Agent Runtime.
    """
    logger.info(f"Executing tool '{request.tool_slug}'", extra_data={"execution_id": request.execution_id})
    return await execution_engine.execute(request)