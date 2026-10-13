from uuid import UUID

from packages.events.base import BaseEvent


class AgentRuntimeLifecycleEvent(BaseEvent):
    id: UUID

class AgentRunStartedEvent(AgentRuntimeLifecycleEvent):
    @property
    def subject(self)-> str:
        return "agent_runtime.events.run.started"

class AgentRunCompletedEvent(AgentRuntimeLifecycleEvent):
    @property
    def subject(self)-> str:
        return "agent_runtime.events.run.completed"

class AgentRunFailedEvent(AgentRuntimeLifecycleEvent):
    @property
    def subject(self)-> str:
        return "agent_runtime.events.run.failed"

class AgentStateInactiveEvent(AgentRuntimeLifecycleEvent):
    @property
    def subject(self)-> str:
        return "agent_runtime.events.agent.inactive"

class AgentStateNotFoundEvent(AgentRuntimeLifecycleEvent):
    @property
    def subject(self)-> str:
        return "agent_runtime.events.agent.not_found"
