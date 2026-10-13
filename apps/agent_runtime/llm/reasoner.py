from typing import List, Dict, Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage

from apps.agent_runtime.application.runtime.context import ExecutionContext
from apps.agent_runtime.domain.actions import AgentDecision
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger


class Reasoner:
    def __init__(self, llm: BaseChatModel):
        self.structured_llm = llm.with_structured_output(AgentDecision)

    def _build_system_prompt(
                self,
                available_tools: List[Dict[str, Any]],
                current_plan: Optional[Dict[str, Any]],
                previous_observations: Optional[List[str]]) -> str:

            tools_summary = "\n".join([f"- {t.get('name')}: {t.get('description')}" for t in available_tools])

            return f"""You are an autonomous agent execution engine core. 
            You do not execute actions directly. You analyze state and return a structured decision.

            AVAILABLE TOOLS:
            {tools_summary}
        
            CURRENT PLAN:
            {current_plan or "No active plan."}
        
            PREVIOUS OBSERVATIONS:
            {previous_observations or "None"}
        
            You must select an action type: FINAL_RESPONSE, CALL_TOOL, CALL_AGENT, CREATE_PLAN, WAIT, or REQUEST_APPROVAL.
            Provide clear reasoning in your thought field.
            """

    async def decide(self, context: ExecutionContext,
                     messages: List[BaseMessage],
                     available_tools: List[Dict[str, Any]],
                     current_plan: Optional[Dict[str, Any]] = None,
                     previous_observations : Optional[List[str]] = None
                     )-> AgentDecision:
        """
        Receives context, memory, tools, observations, and plan.
        It queries the LLM to return a validated AgentDecision.
        """
        logger.info(f"Reasoner evaluating the state for run {context.run_id}")
        system_prompt = self._build_system_prompt(available_tools, current_plan, previous_observations)
        full_prompt = [SystemMessage(content=system_prompt)] + messages

        try:
            decision: AgentDecision = await self.structured_llm.ainvoke(full_prompt)
            logger.info(f"Decision reached: {decision.action_type.value}")
            return decision
        except Exception as e:
            logger.execution(f"Failed to parse structured LLM decision: {str(e)}")
            raise RuntimeError(f"Reasoner failure: {str(e)}")