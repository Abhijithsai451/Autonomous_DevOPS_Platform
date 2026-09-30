import time
from typing import Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from apps.agent_runtime.application.execution_service import AgentExecutionService
from apps.agent_runtime.domain.processed_event import ProcessedEvent
from apps.agent_runtime.infrastructure.database import agent_db_session
from apps.agent_runtime.infrastructure.telemetry import AgentObservability
from packages.logging.structured_logs import struc_logger as logger

CONSUMER_GROUP = "agent_runtime_task_consumer"

async def handle_task_event(payload: Dict[str, Any], metadata: Dict[str, Any]) -> None:
    event_id = UUID(payload["event_id"])
    task_id = UUID(payload["task_id"])
    workflow_instance_id = UUID(payload["workflow_instance_id"])
    agent_id = UUID(payload["agent_id"])
    input_data = payload.get("input_data", {})

    parent_ctx = AgentObservability.extract_trace_context(metadata.get("headers", {}))
    start_time = time.perf_counter()
    status = "SUCCESS"

    with AgentObservability.trace_agent_run(agent_id = str(agent_id),
                                            agent_type="LangGraphAgent",
                                            workflow_instance_id=str(workflow_instance_id),
                                            parent_context=parent_ctx):
        db_gen = agent_db_session()
        db: Session = next(db_gen)

        try:
            processed_event = ProcessedEvent(
                event_id = event_id,
                consumer_group = CONSUMER_GROUP,
            )
            db.add(processed_event)
            db.flush()

            execution_service = AgentExecutionService(db)
            execution_service.execute_task(
                task_id = task_id,
                workflow_instance_id=workflow_instance_id,
                agent_id=agent_id,
                input_data=input_data,
            )
            logger.info(f"Successfully Executed task {task_id} for event {event_id}")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            duration = time.perf_counter() - start_time
            AgentObservability.record_metrics(
                                            agent_type="agent_type",
                                            status = status,
                                            duration = duration
                                            )
            try:
                next(db_gen)
            except StopIteration:
                pass
