import time
from datetime import timezone, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from apps.agent_runtime.domain.agent_runs import AgentRuns
from apps.agent_runtime.domain.agents import Agent
from apps.agent_runtime.repository.agent_repository import AgentRepository
from apps.agent_runtime.repository.outbox_repository import OutboxRepository
from apps.workflow.domain.outbox import OutboxEvent


class AgentRuntimeEngine:
    def __init__(self,  db: Session):
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.outbox_repo = OutboxRepository(db)

    async def execute(self, agent_id: UUID, task_id: UUID, workflow_instance_id: UUID, input_data: dict):
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
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found")

        run_id = UUID()
        start_time = time.time()
        started_at = datetime.now(timezone.utc)

        agent_run = AgentRuns(id = run_id,
                              task_id = task_id,
                              workflow_instance_id= workflow_instance_id,
                              input_data = input_data,
                              started_at = started_at
                              )
        self.db.add(agent_run)
        self.db.flush()




