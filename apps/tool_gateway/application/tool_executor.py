import asyncio
import time
from typing import Any, Dict

from apps.tool_gateway.application import tool_registry
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger


class ToolExecutionResult:
    def __init__(self, success: bool, output: Any = None, error: str = None, duration_ms: float = 0.0):
        self.success = success
        self.output = output
        self.error = error
        self.duration_ms = duration_ms

class ToolExecutor:
    @staticmethod
    async def execute_tool(tool_name: str, raw_arguments: Dict[str, Any], tenant_id: str = None)-> ToolExecutionResult:
        """
        Tool Executor is reponsible for
        1. Safely executing a tool
        2. Validates inputs against schema
        3. Enforces timeout limits.
        4. Handles logging and errors.
        """
        start_time = time.perf_counter()
        try:
            tool = tool_registry.get_tool(tool_name)
        except Exception as e:
            return ToolExecutionResult(success = False, error = str(e))

        try:
            validated_args = tool.args_schema(**raw_arguments).model_dump()
        except Exception as validation_err:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Validation failed for tool {tool_name}: {str(validation_err)}")
            return ToolExecutionResult(success=False, error=f"Invalid arguments: {str(validation_err)}",
                                       duration_ms=duration_ms)

        logger.info(f"Executing tool {tool_name} with risk level {tool_name}")

        try:
            async with asyncio.timeout(tool.timeout_seconds):
                result = await tool.execute(validated_args)

            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolExecutionResult(success=True, output=result, duration_ms=duration_ms)

        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Tool {tool_name} timed out after {tool.timeout_seconds}s")
            return ToolExecutionResult(success=False, error=f"Tool execution timed out after {tool.timeout_seconds}s",
                                       duration_ms=duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception(f"Error executing tool {tool_name}: {str(e)}")
            return ToolExecutionResult(success=False, error=str(e), duration_ms=duration_ms)