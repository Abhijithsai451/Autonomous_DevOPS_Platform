import asyncio
import time

from apps.tool_gateway.application.registry import ToolRegistry
from apps.tool_gateway.domain.tool_execution_result import ToolExecutionResult, ToolExecutionStatus
from apps.tool_gateway.domain.tool_execution_request import ToolExecutionRequest
import asyncio
import time

from apps.tool_gateway.infrastructure.composio_adapter import composio_adapter
from apps.tool_gateway.infrastructure.opa_client import auth_engine
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger


class ToolExecutionEngine:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        start_time = time.perf_counter()

        # 1. Security & Authorization Gate
        authorized = await auth_engine.is_authorized(request)
        if not authorized:
            duration = int((time.perf_counter() - start_time) * 1000)
            return ToolExecutionResult(
                execution_id=request.execution_id,
                status=ToolExecutionStatus.UNAUTHORIZED,
                error_message=f"Execution denied by authorization policy for tool '{request.tool_slug}'",
                duration_ms=duration
            )

        tool = self.registry.get_tool(request.tool_slug)

        if tool:
            try:
                tool.validate_input(request.input_data)
                output = await asyncio.wait_for(
                    tool.run(request.input_data),
                    timeout=float(request.timeout_seconds)
                )
                duration = int((time.perf_counter() - start_time) * 1000)
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=ToolExecutionStatus.SUCCESS,
                    output=output,
                    duration_ms=duration
                )
            except ValueError as ve:
                duration = int((time.perf_counter() - start_time) * 1000)
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=ToolExecutionStatus.INVALID_INPUT,
                    error_message=str(ve),
                    duration_ms=duration
                )
            except asyncio.TimeoutError:
                duration = int((time.perf_counter() - start_time) * 1000)
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=ToolExecutionStatus.TIMEOUT,
                    error_message=f"Execution timed out after {request.timeout_seconds}s",
                    duration_ms=duration
                )
            except Exception as ex:
                duration = int((time.perf_counter() - start_time) * 1000)
                logger.error(f"Error executing local tool '{request.tool_slug}': {ex}", exc_info=True)
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=ToolExecutionStatus.FAILED,
                    error_message=str(ex),
                    duration_ms=duration
                )

        if "." in request.tool_slug:
            try:
                composio_result = await asyncio.wait_for(
                    composio_adapter.execute_action(
                        action_name=request.tool_slug,
                        input_data=request.input_data,
                        connected_account_id=request.connected_account_id
                    ),
                    timeout=float(request.timeout_seconds)
                )
                duration = int((time.perf_counter() - start_time) * 1000)
                status = ToolExecutionStatus.SUCCESS if composio_result.get("success") else ToolExecutionStatus.FAILED
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=status,
                    output=composio_result.get("data", {}),
                    error_message=composio_result.get("error"),
                    duration_ms=duration
                )
            except asyncio.TimeoutError:
                duration = int((time.perf_counter() - start_time) * 1000)
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=ToolExecutionStatus.TIMEOUT,
                    error_message="Composio tool call timed out.",
                    duration_ms=duration
                )
            except Exception as ex:
                duration = int((time.perf_counter() - start_time) * 1000)
                return ToolExecutionResult(
                    execution_id=request.execution_id,
                    status=ToolExecutionStatus.FAILED,
                    error_message=f"Composio execution error: {str(ex)}",
                    duration_ms=duration
                )

        duration = int((time.perf_counter() - start_time) * 1000)
        return ToolExecutionResult(
            execution_id=request.execution_id,
            status=ToolExecutionStatus.NOT_FOUND,
            error_message=f"Tool '{request.tool_slug}' not recognized.",
            duration_ms=duration
        )