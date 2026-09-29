import time
from datetime import timezone, datetime
from uuid import UUID, uuid4

from langgraph.types import Command
from sqlalchemy.orm import Session

from apps.agent_runtime.agents.langgraph_agent import LangGraphAgent
from apps.agent_runtime.domain.agent_contract import AgentContext, AgentExecutionStatus
from apps.agent_runtime.domain.agent_runs import AgentRuns, RunStatus
from apps.agent_runtime.graphs.base_graph import build_base_agent_graph
from apps.agent_runtime.infrastructure.checkpoint import get_postgres_checkpointer
from apps.agent_runtime.repository.agent_repository import AgentRepository
from apps.agent_runtime.repository.outbox_repository import OutboxRepository


class AgentExecutionService:
    def __init__(self, db: Session):
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.outbox_repo = OutboxRepository(db)
        self.agent_executor = LangGraphAgent()

    def execute_task(self, task_id: UUID, workflow_instance_id: UUID, agent_id: UUID, input_data: dict)-> AgentRuns:
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent with the {agent_id} not found")

        run_id = uuid4()
        start_time = time.time()
        started_at = datetime.now(timezone.utc)

        agent_run = AgentRuns(id = run_id,
                              agent_id = agent.id,
                              task_id = task_id,
                              workflow_instance_id= workflow_instance_id,
                              status = RunStatus.RUNNING,
                              input_data = input_data,
                              started_at = started_at
                              )
        self.db.add(agent_run)
        self.db.flush()

        context = AgentContext(run_id = run_id,
                               agent_id = agent_id,
                               task_id = task_id,
                               workflow_instance_id = workflow_instance_id,
                               input_data = input_data,
                               configuration = agent.configuration or {}
        )

        result = self.agent_executor.execute(context)

        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc)

        agent_run.duration_ms = duration_ms
        agent_run.completed_at = completed_at

        if result.status == AgentExecutionStatus.COMPLETED:
            agent_run.status = AgentExecutionStatus.COMPLETED
            agent_run.output_data = result.output_data
        else:
            agent_run.status = AgentExecutionStatus.FAILED
            agent_run.error = (
                {"code": result.error.code,
                 "message": result.error.message}
                if result.error
        else {"message": "Unknown Error"}
            )

        output_payload = {
            "run_id": str(agent_run.id),
            "agent_id": str(agent_run.agent_id),
            "task_id": str(agent_run.task_id),
            "workflow_instance_id": str(agent_run.workflow_instance_id),
            "status": agent_run.status.value,
            "output_data": agent_run.output_data,
            "error": agent_run.error,
            "duration_ms": duration_ms,
        }

        self.outbox_repo.create_event(
            event_type = "agent_runtime.events.agent.finished",
            aggregate_type = "AgentRun",
            aggregate_id = agent_run.id,
            payload = output_payload
        )

        self.db.commit()
        return agent_run

    def resume_execution(self, run_id: str, approved: bool, reason: str = "")-> dict:
        config = {"configurable": {"thread_id": str(run_id)}}

        with get_postgres_checkpointer() as checkpointer:
            graph = build_base_agent_graph(checkpointer = checkpointer)

            final_state = graph.invoke(
                Command(resume = {"approved":approved, "reason": reason}),
                config = config
            )
        return final_state
    

