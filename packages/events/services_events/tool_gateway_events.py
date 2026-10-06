from uuid import UUID

from packages.events.base import BaseEvent


class ToolGatewayLifecycleEvent(BaseEvent):
    id: UUID

