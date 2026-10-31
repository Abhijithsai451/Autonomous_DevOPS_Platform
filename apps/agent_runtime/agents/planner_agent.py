import json
from typing import Any, Dict

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.llm.prompts.planner_prompt import build_planner_prompt, planner_system_prompt


class PlannerAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        self.system_prompt = planner_system_prompt
    async def execute(self,task_spec: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Planner: Building prompt and invoking LLM")
        prompt = build_planner_prompt(task_spec)

        response = await self.model.aexecute(
            message=prompt,
            system_prompt=self.system_prompt,
        )
        print(response)

        try:
            clean_json = response.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.warning(f"Planner: Failed to parse LLM response JSON: {e}")
            return {
                "plan_title": task_spec.get("project_title", "Engineering Plan (Fallback)"),
                "architecture_summary": task_spec.get("executive_summary", ""),
                "tasks": [
                    {
                        "task_id": "TASK-1",
                        "layer": "BACKEND",
                        "title": "Implement core requirement",
                        "description": str(task_spec.get("in_scope", ["Implement user request"])),
                        "target_files": [],
                        "depends_on": [],
                    }
                ],
                "testing_strategy": "Implement unit and integration tests.",
            }

    async def planner_node(self, state: AgentContext) -> AgentContext:
        logger.info(f"[Node: planner] Generating implementation plan")
        task_spec = state.data.get("task_specification")
        if not task_spec:
            logger.warning("[Node: Planner] No task_specification found in input_data; falling back to state.prompt")
            task_spec = {
                "project_title": "Ad-hoc Plan",
                "executive_summary": state.prompt,
                "in_scope": [state.prompt],
            }

        plan = await self.execute(task_spec)

        state.data["execution_plan"] = plan
        state.data["tasks"] = plan.get("tasks", [])
        state.data["status"] = "PLANNING_COMPLETED"

        task_count = len(plan.get("tasks", []))
        logger.info(f"[Node: Planner] Plan created with {task_count} tasks: '{plan.get('plan_title')}'")
        return state


