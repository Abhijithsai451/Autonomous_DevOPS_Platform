from contextlib import asynccontextmanager
from fastapi import FastAPI

from apps.tool_gateway.api import health
from apps.tool_gateway.application.executor import ToolExecutionEngine
from apps.tool_gateway.application.registry import tool_registry
from apps.tool_gateway.domain.tool_execution_request import ToolExecutionRequest
from apps.tool_gateway.domain.tool_execution_result import ToolExecutionResult
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger
from apps.tool_gateway.tools.echo import EchoTool
from apps.tool_gateway.tools.http_request import HttpRequestTool
from apps.tool_gateway.tools.json_transform import JsonTransformTool


def register_default_tools():
    tool_registry.register(EchoTool())
    tool_registry.register(JsonTransformTool())
    tool_registry.register(HttpRequestTool())


@asynccontextmanager
async def tool_gateway_lifespan(app: FastAPI):
    logger.info("Initializing Tool Gateway Service Daemon....")
    register_default_tools()
    logger.info("Tool Registry populated with default tools: echo, json_transform, http_request.")

    yield

    logger.info("Tool Gateway Service shutdown complete.")


app = FastAPI(title="CortexOps Tool Gateway Service", lifespan=tool_gateway_lifespan)

app.include_router(health.router)

execution_engine = ToolExecutionEngine(tool_registry)


@app.post("/api/v1/tools/execute", response_model=ToolExecutionResult)
async def execute_tool(request: ToolExecutionRequest):
    """
    Standardized execution boundary endpoint called by Agent Runtime.
    """
    logger.info(f"Executing tool '{request.tool_slug}'", extra_data={"execution_id": request.execution_id})
    return await execution_engine.execute(request)