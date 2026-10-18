import asyncio
from contextlib import asynccontextmanager
from urllib.request import Request

from fastapi import FastAPI
from sqlalchemy.orm.exc import StaleDataError
from starlette.responses import JSONResponse

from apps.agent_runtime.infrastructure.outbox_publisher import agent_outbox_publisher
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.infrastructure.database import agent_db_session as db_client
from apps.agent_runtime.workers.task_consumer import task_event_handler
from packages.redis.redis_client import redis_client
from apps.agent_runtime.infrastructure.agent_runtime_nats_client import agent_nats_client as nats

async def department_created_event_handler(payload: dict, metadata: dict):
    dept_id = payload.get("id")
    description = payload.get("description")

    logger.info(f"  Workflow Service received DepartmentCreated: Dept ID={dept_id}, Description='{description}'")

@asynccontextmanager
async def agent_runtime_lifespan(app: FastAPI):
    await redis_client.initialize()

    await nats.initialize()
    logger.info("NATS Messaging Core successfully initialized.")
    await nats.client.ensure_stream(stream_name="workflow_events", subjects=['workflow.events.task.>'])

    outbox_task = asyncio.create_task(agent_outbox_publisher.start())
    logger.info("Outbox Publisher Worker started successfully.")
    durable_name = "workflow-events-task-ready"

    await nats.register_listener(subject = "Agent_runtime_initiated",
                                 durable_name= durable_name,
                                 handler = task_event_handler,
                                 stream = "workflow_events"
                                 )

    yield

    agent_outbox_publisher.stop()
    await outbox_task

    await nats.shutdown()
    await redis_client.close()
    logger.info("NATS Messaging Core successfully disconnected.")

app = FastAPI(title="ADD_Platform Agent Runtime Service", lifespan= agent_runtime_lifespan)

@app.exception_handler(StaleDataError)
async def stale_data_exception_handler(request: Request, exc: StaleDataError):
    """
    Catches concurrent Mutation race conditions (SQL Alchemy Conflicts)
    Turns DB Errors into a clean HTTP 409 Conflict response.
    """
    logger.warning(f"Optimistic lock conflict detected: {exc}")
    return JSONResponse(
        status_code = 409,
        content = {
            "error" : "RESOURCE_CONFLICT",
            "message": "The resource was updated by another request. Please retry your operation."
        }
    )
