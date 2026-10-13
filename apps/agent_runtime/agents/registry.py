from typing import List, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    agent_id : UUID
    name: str
    capabilities: List[str] = Field(default_factory = list)
    system_prompt: str
    is_active: bool = True

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[UUID, AgentProfile] = {}

    def register(self, profile: AgentProfile)-> None:
        self._agents[profile.agent_id]= profile

    def find_by_capability(self, capability: str)-> List[AgentProfile]:
        return [agent for agent in self._agent.values() if capability in agent.capabilities and agent.is_active]


