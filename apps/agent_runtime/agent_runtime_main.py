import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm.exc import StaleDataError

from apps.agent_runtime.api import health
from apps.agent_runtime.infrastructure.agent_runtime_nats_client import agent_nats_client as nats
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client
from apps.agent_runtime.infrastructure.outbox_publisher import agent_outbox_publisher
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.infrastructure.telemetry import AgentObservability
from apps.agent_runtime.workers.task_handler import handle_task_event
from packages.redis.redis_client import redis_client
from packages.telemetry.provider import init_telemetry


@asynccontextmanager
async def agent_lifespan(app: FastAPI):
    if not agent_runtime_db_client.check_health():
        raise RuntimeError("Agent Runtime database health check failed on startup!")
    init_telemetry(service_name="cortexops-agent-runtime", environment="local")
    logger.info("Initializing the Agent Runtime Daemon ....")

    await redis_client.initialize()
    await nats.initialize()
    logger.info("NATS Core Messaging is successfully initialized for Agent Runtime Service")

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

@app.post("/api/v1/agents/execute")
async def execute_agent(payload: dict):
    """
    Direct REST endpoint trigger for agent execution (mirrors consumer execution).
    """
    agent_id = payload.get("agent_id")
    task_id = payload.get("task_id")
    workflow_instance_id = payload.get("workflow_instance_id")
    input_data = payload.get("input_data", {})
    agent_type = payload.get("agent_type", "LangGraphAgent")

    start_time = time.perf_counter()
    status = "success"

    with AgentObservability.trace_agent_run(
                                        agent_id=str(agent_id),
                                        agent_type=agent_type,
                                        tenant_id=payload.get("tenant_id"),
                                        workflow_instance_id=str(workflow_instance_id),
                                        agent_run_id=payload.get("agent_run_id"),
                                        ):
        db_gen = agent_runtime_db_client.get_db()
        db = next(db_gen)
        try:
            logger.info("Agent starting execution", extra_data={"agent_type": agent_type})

            from apps.agent_runtime.application.execution_service import AgentExecutionService
            execution_service = AgentExecutionService(db)

            run_result = execution_service.execute_task(
                                                task_id=task_id,
                                                workflow_instance_id=workflow_instance_id,
                                                agent_id=agent_id,
                                                input_data=input_data,
            )

            logger.info("Agent completed task execution")
            return {
                    "status": "ok",
                    "run_id": str(run_result.id),
                    "run_status": run_result.status.value,
                    "output_data": run_result.output_data,
                }

        except Exception as exc:
            status = "failure"
            logger.error(f"Agent execution failed: {str(exc)}", exc_info=True)
            raise exc

        finally:
            duration = time.perf_counter() - start_time
            AgentObservability.record_metrics(
                                            agent_type=agent_type,
                                            status=status,
                                            duration=duration,
                                            prompt_tokens=0,
                                            completion_tokens=0,
                                         )
            try:
                next(db_gen)
            except StopIteration:
                pass


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


app.include_router(health.router)