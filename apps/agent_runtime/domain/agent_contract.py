from dataclasses import dataclass, field
from typing import Any, Annotated

from sqlalchemy import String, Column, Text, JSON

from apps.agent_runtime.infrastructure.base import Base

def merge_dicts(old: dict, new: dict) -> dict:
    """Custom reducer to safely merge dictionaries without overwriting disjoint keys."""
    return {**(old or {}), **(new or {})}

@dataclass()
class AgentContext:
    task_id: str
    workflow_instance_id: str | None
    run_id: str
    prompt: str
    data: Annotated[dict[str, Any], merge_dicts] = field(default_factory=dict)
    agent_configuration: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class AgentResult:
    output_data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

class AgentResolutionError(Exception):
    """Raised when an agent cannot be resolved from its configuration."""


class AgentSelectionError(Exception):
    """Raised when no suitable active agent can be selected."""


class AgentContextModel(Base):
    __tablename__ = "agent_context"
    __table_args__ = {"schema":"agent_runtime"}

    task_id = Column(String, primary_key=True, index=True)
    workflow_instance_id = Column(String, nullable=True, index=True)
    run_id = Column(String, index=True, nullable=False)
    prompt = Column(Text, nullable=False)

    data = Column(JSON, default=dict, nullable=False)
    agent_configuration = Column(JSON, default=dict, nullable=False)

    @classmethod
    def from_dataclass(cls, ctx: AgentContext) -> "AgentContextModel":
        """Maps runtime dataclass to the database ORM model."""
        return cls(
            task_id=ctx.task_id,
            workflow_instance_id=ctx.workflow_instance_id,
            run_id=ctx.run_id,
            prompt=ctx.prompt,
            data=ctx.data,
            agent_configuration=ctx.agent_configuration
        )

    def to_dataclass(self) -> AgentContext:
        """Converts the database ORM model back to the runtime dataclass."""
        return AgentContext(
            task_id=self.task_id,
            workflow_instance_id=self.workflow_instance_id,
            run_id=self.run_id,
            prompt=self.prompt,
            data=self.data,
            agent_configuration=self.agent_configuration
        )