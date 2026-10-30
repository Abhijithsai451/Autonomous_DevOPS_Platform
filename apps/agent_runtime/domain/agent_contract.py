from dataclasses import dataclass, field
from typing import Any

@dataclass()
class AgentContext:
    task_id: str
    workflow_instance_id: str | None
    run_id: str
    prompt: str
    data: dict[str, Any] = field(default_factory=dict)
    agent_configuration: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    output_data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentResolutionError(Exception):
    """Raised when an agent cannot be resolved from its configuration."""


class AgentSelectionError(Exception):
    """Raised when no suitable active agent can be selected."""
