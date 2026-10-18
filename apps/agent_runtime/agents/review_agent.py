from typing import Dict, Any
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.llm.prompts.review_prompt import review_prompt


class ReviewAgent(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="code-review-agent", agent_type="review_agent")
        self.model = llm_model
        self.prompt = review_prompt
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        input = state["prompt"]
        response = self.model.run(input)
        state['prompt'] = response

        return state

    async def review_node(self, state: AgentContext) -> AgentContext:
        logger.info("==> [Node: reviewer] Reviewing generated code artifacts...")
        await self.reviewer(state)

        artifacts = state.input_data.get("code_artifacts", {})
        iteration = state.input_data.get("review_iterations", 0) + 1

        has_healthz = "/healthz" in artifacts.get("server/main.py", "")
        has_manifests = any("k8s" in path or "deploy" in path or "Dockerfile" in path for path in artifacts.keys())
        is_approved = has_healthz and has_manifests

        comments = state.input_data.setdefault("review_comments", [])
        if is_approved:
            comments.append("Review approved: Specifications met.")
        else:
            comments.append("Review rejected: Missing healthz or deployment manifests.")

        # Direct in-place mutations
        state.input_data["is_review_approved"] = is_approved
        state.input_data["review_iterations"] = iteration
        state.input_data["status"] = "APPROVED" if is_approved else "NEEDS_REVISION"
        return state

    def _route_after_review(self, state: AgentContext) -> str:
        if state.input_data.get("is_review_approved", False):
            logger.info("==> [Router] Code approved. Routing to deployer.")
            return "deployer"
        if state.input_data.get("review_iterations", 0) >= 3:
            logger.warning("==> [Router] Max review iterations reached. Terminating.")
            return "failed"
        logger.info("==> [Router] Revision requested. Routing back to code_orchestrator.")
        return "code_orchestrator"