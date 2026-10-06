from uuid import UUID

from packages.events.base import BaseEvent


class AgentRuntimeLifecycleEvent(BaseEvent):
    id: UUID

