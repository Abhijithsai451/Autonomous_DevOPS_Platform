
from typing import List
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

class PlanStep(BaseModel):
    step_number: int
    task_description: str
    required_capability: str = Field( description="The capability required (e.g., coding, testing, security_analysis, deployment)")

class AgentPlan(BaseModel):
    goal: str
    steps: List[PlanStep]

class PlannerAgent:
    def __init__(self, llm: BaseChatModel):
        self.structured_llm = llm.with_structured_output(AgentPlan)

    async def create_plan(self, user_goal: str) -> AgentPlan:
        """
        Converts a high-level user goal into an executable multi-step plan.
        """
        logger.info(f"Planner generating execution plan for goal: '{user_goal}'")

        system_prompt = """You are an expert Software Architecture Planner. 
                        Your job is to break down a high-level user goal into a sequential, multi-step plan.
                        Assign a specific required capability to each step 
                        (e.g., coding, testing, security_analysis, deployment)."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User Goal: {user_goal}")
        ]

        plan: AgentPlan = await self.structured_llm.ainvoke(messages)
        logger.info(f"Generated plan with {len(plan.steps)} steps.")
        return plan