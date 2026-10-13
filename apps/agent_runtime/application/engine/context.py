from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import UUID


@dataclass
class ExecutionContext:
    agent_id: UUID
    task_id: UUID
    workflow_instance_id: UUID
    input_data: Dict[str, Any]
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    run_id: Optional[UUID] = None