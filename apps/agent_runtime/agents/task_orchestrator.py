import json
from typing import Dict, Any
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts.task_orchestrator_prompt import task_orchestrator_system_prompt, build_task_orchestrator_prompt
from apps.agent_runtime.repository.rag_repository import KBRepository


class TaskOrchestrator(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        self.system_prompt = task_orchestrator_system_prompt

    async def execute(self, user_request)-> Dict[str, Any]:
        logger.info("Agent Prompt Created and Invoking the LLM")
        context = ""
        try:
            with next(db_client.get_session()) as session:
                repo = KBRepository(db=session)
                context = await repo.retrieve_context(user_request, 3)
        except Exception as ex:
            logger.warning(f"Task Orchestrator: Failed to retrieve RAG context: {ex}")

        prompt = build_task_orchestrator_prompt(user_request, context)
        response = await self.model.aexecute(
            message = prompt,
            system_prompt=self.system_prompt,
        )
        #print(response)
        try:
            clean_json = response.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.warning(f"Task Orchestrator: Failed to parse LLM response JSON: {e}")
            return {
                "project_title": "Task Specification (Fallback)",
                "executive_summary": user_request,
                "domains_impacted": [],
                "technical_components": [],
                "in_scope": [user_request],
                "out_of_scope": [],
                "architectural_constraints": [],
                "acceptance_criteria": ["Verify user request is met."],
            }

    async def task_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info(f"==> [Node: Task Orchestrator] Analyzing prompt: '{state.prompt}'")
        triage_data = state.input_data.get("summary")
        if isinstance(triage_data, dict):
            query = triage_data.get("sanitized_summary") or state.prompt
        elif isinstance(triage_data, str) and triage_data:
            query = triage_data
        else:
            query = state.prompt
        specification  = await self.execute(query)

        state.input_data["task_specification"] = specification
        state.input_data["status"] = "TASK_ORCHESTRATION_COMPLETED"
        logger.info(f"==> [Node: Task Orchestrator] Specification created: '{specification.get('project_title')}'")

        return state
