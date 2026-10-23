from typing import Optional, Dict, Any

from langgraph.checkpoint.redis import RedisSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from apps.agent_runtime.agents.code_orchestrator import CodeOrchestratorAgent
from apps.agent_runtime.agents.deploy_agent import DeployAgent
from apps.agent_runtime.agents.planner_agent import PlannerAgent
from apps.agent_runtime.agents.review_agent import ReviewAgent
from apps.agent_runtime.agents.task_orchestrator import TaskOrchestrator
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.redis_client import agent_redis_client
from apps.agent_runtime.llm.llm_config import LLMClient


class AgentGraph:
    def __init__(self):
        self.redis_client = agent_redis_client
        self.checkpointer = RedisSaver(redis_client=self.redis_client.redis)
        self.llm = LLMClient()

        #Agents
        self.task_orchestrator = TaskOrchestrator(self.llm)
        self.planner = PlannerAgent(self.llm)
        self.code_orchestrator = CodeOrchestratorAgent(self.llm)
        self.reviewer = ReviewAgent(self.llm)
        self.deployer = DeployAgent(self.llm)

        self.workflow = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentContext)
        #Nodes
        graph.add_node("task_orchestrator", self.task_orchestrator)
        graph.add_node("planner", self.planner.planner_node)
        graph.add_node("code_orchestrator", self.code_orchestrator.code_orchestrator_node)
        graph.add_node("reviewer", self.reviewer.review_node)
        graph.add_node("deployer", self.deployer.deploy_node)

        #Edges
        graph.set_entry_point("task_orchestrator")
        graph.add_edge("task_orchestrator","planner")
        graph.add_edge("planner", "code_orchestrator")
        graph.add_edge("code_orchestrator", "reviewer")

        graph.add_conditional_edges(
            "reviewer",
            self.reviewer._route_after_review,
            {
                "deployer": "deployer",
                "code_orchestrator": "code_orchestrator",
                "failed": END,
            },
        )
        graph.add_edge("deployer", END)

        return graph.compile()

    async def ainvoke(self, initial_state: AgentContext, config: Optional[Dict[str, Any]] = None) -> AgentContext:
        return await self.workflow.ainvoke(initial_state, config=config)





