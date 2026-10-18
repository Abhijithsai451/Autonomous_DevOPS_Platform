from typing import Dict, Any

from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.llm.prompts.code_orchestrator_prompt import backend_prompt


class BackendAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-backend-agent", agent_type="backend_agent")
        self.model = llm_model
        self.prompt = backend_prompt
    async def execute(self, state: AgentContext)-> Dict[str, Any]:
        return {
            "code_artifacts": {
                "server/main.py": (
                    "from fastapi import FastAPI\n"
                    "app = FastAPI()\n\n"
                    "@app.get('/healthz')\n"
                    "def health(): return {'status': 'ok'}\n"
                )
            }
        }

    def backend_node(self, ctx:AgentContext):
        pass