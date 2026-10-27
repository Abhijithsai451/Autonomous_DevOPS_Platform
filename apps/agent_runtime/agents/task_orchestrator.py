from typing import Dict, Any
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts import task_orchestrator_prompt
from apps.agent_runtime.repository.rag_repository import KBRepository


class TaskOrchestrator(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        #self.prompt = task_orchestrator_prompt.build_prompt()

    async def execute(self, prompt)-> Dict[str, Any]:
        logger.info("Executing the LLM with the query")
        output = self.model.execute(prompt)
        return output

    async def task_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info(f"==> [Node: Task Orchestrator] Analyzing prompt: '{state.prompt}'")
        query = state.prompt
        with next(agent_runtime_db_client.get_session()) as session:
            repo = KBRepository(db=session)
            context = await repo.retrieve_context(query, 3)
            prompt = task_orchestrator_prompt(query, context)
            output = await self.execute(prompt)
            state.output = output
        return state
