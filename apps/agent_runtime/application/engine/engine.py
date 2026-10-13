import time
from datetime import timezone, datetime
from typing import Callable

from sqlalchemy.orm import Session

from apps.agent_runtime.application.runtime.context import ExecutionContext
from apps.agent_runtime.domain.agent_contract import AgentResult, AgentError, AgentExecutionStatus
from apps.agent_runtime.domain.agent_runs import AgentRuns
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.infrastructure.telemetry import AgentObservability
from apps.agent_runtime.repository.agent_repository import AgentRepository
from apps.agent_runtime.repository.agent_run_repository import AgentRunsRepository
from apps.agent_runtime.repository.outbox_repository import OutboxRepository
from packages.events.services_events.agent_runtime_events import AgentStateNotFoundEvent, AgentStateInactiveEvent, \
    AgentRunStartedEvent, AgentRunFailedEvent, AgentRunCompletedEvent


class AgentRuntimeEngine:
    def __init__(self,  db: Session):
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.run_repo = AgentRunsRepository(db)
        self.outbox_repo = OutboxRepository(db)

    async def execute(self, context: ExecutionContext, agent_executor : Callable[[ExecutionContext], AgentResult])-> AgentResult:
        """
        Execution Engine is responsible for
        1. Load Agent
        2. Create execution context
        3. Start AgentRun
        4. Execute Agent
        5. Capture Result
        6. Persist State
        7. Emit events
        8. Handle Failures
        9. Finish Execution
        """
        start_time = time.perf_counter()
        try:

            agent = self.agent_repo.get_by_id(context.agent_id)
            if not agent:
                error = AgentError(code = AgentStateNotFoundEvent(id = context.agent_id).subject,message = f"Agent ")
                return AgentResult(status=AgentExecutionStatus.FAILED, error=error)
            if agent.status.value != "ACTIVE":
                error = AgentError(code=AgentStateInactiveEvent(id = context.agent_id).subject, message=f"Agent {context.agent_id} is disabled.", retryable=False)
                return AgentResult(status=AgentExecutionStatus.FAILED, error=error)
            if not context.configuration and agent.configuration:
                context.configuration = agent.configuration

            run = self.run_repo.get_by_task_id(context.task_id)
            if not run:
                run = self.run_repo.create(
                    agent_id = context.agent_id,
                    task_id = context.task_id,
                    workflow_instance_id=context.workflow_instance_id,
                    input_data=context.input_data
                )
            context.run_id = run.id
            self.run_repo.mark_running(context.run_id)

            self.outbox_repo.create_event(
                event_type=AgentRunStartedEvent(id = context.agent_id).subject,
                aggregate_type="agent_run",
                aggregate_id=context.run_id,
                payload={"agent_id": str(context.agent_id), "task_id": str(context.task_id)}
            )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Failed to initialize execution setup for task {context.task_id}: {str(e)}")
            return AgentResult(
                status = AgentExecutionStatus.FAILED,
                error = AgentError(code = "INITIALIZATION_ERROR", message = str(e), retryable=True)
            )
        agent_type = agent.slug
        tenant_id = context.metadata.get("tenant_id")

        try:
            with AgentObservability.trace_agent_run(
                    agent_id=str(context.agent_id),
                    agent_type=agent_type,
                    tenant_id=tenant_id,
                    workflow_instance_id=str(context.workflow_instance_id),
                    agent_run_id=str(context.run_id)
            ):

                result = agent_executor(context)

                duration_ms = (time.perf_counter() - start_time) * 1000.0
                result.execution_duration_ms = duration_ms


                if result.status == AgentExecutionStatus.COMPLETED:
                    self.run_repo.mark_completed(context.run_id, result.output_data or {}, int(duration_ms))
                    self.outbox_repo.create_event(
                        event_type=AgentRunCompletedEvent(id = context.agent_id).subject,
                        aggregate_type="agent_run",
                        aggregate_id=context.run_id,
                        payload={"output": result.output_data}
                    )
                else:
                    error_dict = {
                        "code": result.error.code if result.error else "UNKNOWN_ERROR",
                        "message": result.error.message if result.error else "Execution failed",
                        "details": result.error.details if result.error else {},
                        "retryable": result.error.retryable if result.error else False
                    }
                    self.run_repo.mark_failed(context.run_id, error_dict, int(duration_ms))
                    self.outbox_repo.create_event(
                        event_type=AgentRunFailedEvent(id = context.agent_id).subject,
                        aggregate_type="agent_run",
                        aggregate_id=context.run_id,
                        payload={"error": error_dict}
                    )

                self.db.commit()

                AgentObservability.record_metrics(
                    agent_type=agent_type,
                    status=result.status.value,
                    duration=duration_ms / 1000.0
                )
                return result

        except Exception as e:
            self.db.rollback()
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception(f"Unhandled exception during agent run {context.run_id}: {str(e)}")

            error_dict = {
                "code": "UNHANDLED_EXCEPTION",
                "message": str(e),
                "retryable": True
            }

            try:
                self.run_repo.mark_failed(context.run_id, error_dict, int(duration_ms))
                self.outbox_repo.create_event(
                    event_type=AgentRunFailedEvent(id = context.agent_id).subject,
                    aggregate_type="agent_run",
                    aggregate_id=context.run_id,
                    payload={"error": error_dict}
                )
                self.db.commit()
            except Exception as db_err:
                self.db.rollback()
                logger.error(f"Failed to persist failure state for run {context.run_id}: {str(db_err)}")

            AgentObservability.record_metrics(
                agent_type=agent_type,
                status="FAILED",
                duration=duration_ms / 1000.0
            )

            return AgentResult(
                status=AgentExecutionStatus.FAILED,
                error=AgentError(code="UNHANDLED_EXCEPTION", message=str(e), retryable=True),
                execution_duration_ms=duration_ms
            )




