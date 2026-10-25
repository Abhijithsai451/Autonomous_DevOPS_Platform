from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts.task_orchestrator_prompt import task_orchestrator_prompt


class TaskOrchestrator(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        self.prompt = task_orchestrator_prompt

    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        input = state.prompt
        #response = self.model.run(input)
        logger.info("making an LLM Call")
        state.prompt = "response"

        return state

    async def task_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info(f"==> [Node: Task Orchestrator] Analyzing prompt: '{state.prompt}'")
        output = await self.execute(state)
        """
        state.input_data["tasks"] = output.get("tasks", [
            "Generate backend REST API with healthz check",
            "Generate frontend client UI",
            "Generate Dockerfile and Kubernetes manifests",
        ])
        """
        state.input_data["status"] = "PLANNING_COMPLETED"
        return state
