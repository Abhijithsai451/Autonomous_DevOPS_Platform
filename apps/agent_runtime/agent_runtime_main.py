import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import StaleDataError

from apps.agent_runtime.api import health, execute
from apps.agent_runtime.infrastructure.agent_runtime_nats_client import agent_nats_client as nats
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client
from apps.agent_runtime.infrastructure.outbox_publisher import agent_outbox_publisher
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.infrastructure.telemetry import AgentObservability

from apps.agent_runtime.workers.task_handler import handle_task_event
from packages.redis.redis_client import redis_client
from packages.telemetry.provider import init_telemetry
from apps.agent_runtime.application.execution_service import AgentExecutionService



@asynccontextmanager
async def agent_lifespan(app: FastAPI):
    if not agent_runtime_db_client.check_health():
        raise RuntimeError("Agent Runtime database health check failed on startup!")
    init_telemetry(service_name="cortexops-agent-runtime", environment="local")
    logger.info("Initializing the Agent Runtime Daemon ....")

    await redis_client.initialize()
    await nats.initialize()
    logger.info("NATS Core Messaging is successfully initialized for Agent Runtime Service")

    logger.info("Tool Registry populated with default tools.")

    await nats.register_listener(
        subject = "workflow.events.tasks.ready",
        durable_name = "agent_runtime_task_executor",
        handler = handle_task_event
    )
    logger.info("Registered 'workflow.events.task.ready' consumer listener.")

    outbox_task = asyncio.create_task(agent_outbox_publisher.start())
    logger.info("Agent Runtime Outbox Publisher Worker started successfully.")

    yield

    agent_outbox_publisher.stop()
    await outbox_task
    await nats.shutdown()
    await redis_client.close()

    logger.info("NATS Messaging Core successfully disconnected from Agent Runtime.")

app = FastAPI(title="ADD_Platform Agent Runtime Service", lifespan=agent_lifespan)

app.include_router(execute.router)
app.include_router(health.router)

@app.exception_handler(StaleDataError)
async def stale_data_exception_handler(request: Request, exc: StaleDataError):
    logger.warning(f"Optimistic lock conflict detected in Agent Runtime: {exc}")
    return JSONResponse(
                        status_code=409,
                        content={
                            "error": "RESOURCE_CONFLICT",
                            "message": "The agent runtime resource was updated by another request. Please retry."
                        }
    )