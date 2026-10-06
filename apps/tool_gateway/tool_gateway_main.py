from contextlib import asynccontextmanager
from fastapi import FastAPI

from apps.tool_gateway.api import health, tools
from apps.tool_gateway.application.executor import ToolExecutionEngine
from apps.tool_gateway.application.registry import tool_registry
from apps.tool_gateway.domain.tool_execution_request import ToolExecutionRequest
from apps.tool_gateway.domain.tool_execution_result import ToolExecutionResult
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger
from apps.tool_gateway.infrastructure.tool_gateway_nats_client import tool_gateway_nats_client as nats
from apps.tool_gateway.tools.echo import EchoTool
from apps.tool_gateway.tools.http_request import HttpRequestTool
from apps.tool_gateway.tools.json_transform import JsonTransformTool
from packages.telemetry.provider import init_telemetry


def register_default_tools():
    tool_registry.register(EchoTool())
    tool_registry.register(JsonTransformTool())
    tool_registry.register(HttpRequestTool())


@asynccontextmanager
async def tool_gateway_lifespan(app: FastAPI):
    init_telemetry(service_name="cortexops-tool-gateway", environment = "local")

    logger.info("Initializing Tool Gateway Service Daemon....")

    await nats.initialize()
    logger.info("NATS Core Messaging is successfully initialized for Tool Gateway Service")
    register_default_tools()
    logger.info("Tool Registry populated with default tools")


    yield
    logger.info("Tool Gateway Service shutdown complete.")
    await nats.shutdown()

app = FastAPI(title="CortexOps Tool Gateway Service", lifespan=tool_gateway_lifespan)
app.include_router(health.router)
app.include_router(tools.router)