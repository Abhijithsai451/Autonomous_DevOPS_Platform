from langgraph.checkpoint.redis import RedisSaver

from apps.agent_runtime.agents.code_orchestrator import CodeOrchestratorAgent
from apps.agent_runtime.agents.deploy_agent import DeployAgent
from apps.agent_runtime.agents.planner_agent import PlannerAgent
from apps.agent_runtime.agents.review_agent import ReviewAgent
from apps.agent_runtime.config.settings import agent_runtime_settings as settings
from apps.agent_runtime.infrastructure.redis_client import agent_redis_client
from apps.agent_runtime.llm.llm_config import LLMClient


class AgentGraph:
    def __init__(self):
        self.redi_client = agent_redis_client
        self.checkpointer = RedisSaver(self.redi_client)
        self.llm = LLMClient(model_name = "gpt-4o-mini", api_key=settings.OPENAI_API_KEY)

        self.planner = PlannerAgent(self.llm)
        self.code_orchestrator = CodeOrchestratorAgent(self.llm)
        self.reviewer = ReviewAgent(self.llm)
        self.deployer = DeployAgent(self.llm)




