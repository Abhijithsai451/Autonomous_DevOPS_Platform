import concurrent.futures
from typing import Any, Dict, Optional, Callable
from pydantic import BaseModel, ValidationError
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

class SandboxExecutionError(Exception):
    """Raised when tool execution violates sandbox boundaries or fails."""
    pass

class ToolSandbox:
    """
    Executes tool calls inside a bounded thread pool with timeout enforcement and error shielding.
    """
    def __init__(self, default_timeout_seconds: float = 10.0):
        self.default_timeout = default_timeout_seconds
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=10,
            thread_name_prefix="sandbox_tool_worker",
        )

    def run_sandboxed(
        self,
        func: Callable,
        args: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Executes a function synchronously within time limits and error bounds.
        """
        effective_timeout = timeout or self.default_timeout

        future = self._executor.submit(func, **args)
        try:
            result = future.result(timeout=effective_timeout)
            return result
        except concurrent.futures.TimeoutError:
            logger.error(
                f"Tool execution timed out after {effective_timeout}s"
            )
            raise SandboxExecutionError(
                f"Tool execution timed out after {effective_timeout} seconds."
            )
        except ValidationError as val_err:
            logger.error(f"Tool argument validation failed: {val_err}")
            raise SandboxExecutionError(f"Invalid tool arguments: {val_err}")
        except Exception as exc:
            logger.exception(f"Unhandled error inside tool sandbox: {exc}")
            raise SandboxExecutionError(f"Tool execution failed: {str(exc)}")


# Global sandbox instance
global_sandbox = ToolSandbox(default_timeout_seconds=15.0)