import json
from typing import Dict, Any
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts.gateway_prompt import build_gateway_prompt, gateway_system_prompt
from apps.agent_runtime.repository.rag_repository import KBRepository


class GatewayAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="Gateway-Triage-Agent", agent_type="Gateway")
        self.model = llm_model
        self.system_prompt = gateway_system_prompt
    async def execute(self, user_request)-> Dict[str, Any]:
        prompt = build_gateway_prompt(user_request)
        response = await self.model.aexecute(
            message = prompt,
            system_prompt=self.system_prompt
        )
        print(f"Response from the LLM: {response, None}")
        try:
            clean_json = response.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.warning(f"Failed to parse gateway response JSON: {e}")
            return {
                "summary": user_request,
                "intent": "FEATURE",
                "risk_level": "MEDIUM",
                "route": "full_pipeline",
                "reasoning": "Fallback due to parse error"
            }

    async def gateway_node(self, state: AgentContext) -> AgentContext:
        logger.info(f"==> [Node: Gateway and Triage Agent] Analyzing prompt: '{state.prompt}'")
        triage_result = await self.execute(state.prompt)

        state.input_data["triage"] = triage_result
        state.input_data["route"] = triage_result.get("route", "full_pipeline")

        return state

    def route_after_gateway(self, state: AgentContext)-> str:
        route = state.input_data.get("route", "full_pipeline")

        if route == "BUG_FIX":
            return "bug_fix_subgraph"
        elif route == "ABORT":
            return "abort"
        else:
            return "task_orchestrator"
