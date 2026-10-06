import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.agent_runtime.application.execution_service import AgentExecutionService
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.infrastructure.telemetry import AgentObservability

router = APIRouter(prefix = "/agents", tags = ["execute"])

@router.post("/execute")
async def execute_agent(payload: dict, db: Session = Depends(db_client.get_session)):
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
        db_gen = db_client.get_session()
        db = next(db_gen)
        try:
            logger.info("Agent starting execution", extra_data={"agent_type": agent_type})
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
