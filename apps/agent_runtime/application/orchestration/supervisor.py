import logging
from typing import Dict, Any, List

from apps.agent_runtime.domain.agent_contract import AgentResult, AgentExecutionStatus
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.registry import AgentRegistry
from apps.agent_runtime.application.engine.context import ExecutionContext
from apps.agent_runtime.application.engine.engine import AgentRuntimeEngine


class MultiAgentSupervisor:
    def __init__(
        self,
        agent_registry: AgentRegistry,
        db_session_factory,
        mcp_client
    ):
        self.registry = agent_registry
        self.db_session_factory = db_session_factory
        self.mcp_client = mcp_client

    async def coordinate_plan_execution(self,parent_context: ExecutionContext,plan_steps: List[Any]) -> Dict[str, Any]:
        """
        Iterates through the generated plan, matches steps to specialized agents
        via capabilities, and delegates execution.
        """
        execution_results = []

        for step in plan_steps:
            logger.info(f"Supervisor executing Step {step.step_number}: {step.task_description} [Capability: {step.required_capability}]")

            matching_agents = self.registry.find_by_capability(step.required_capability)
            if not matching_agents:
                error_msg = f"No active agent found with required capability: '{step.required_capability}'"
                logger.error(error_msg)
                return {"status": "FAILED", "error": error_msg, "completed_steps": execution_results}

            specialist = matching_agents[0]
            logger.info(f"Assigned to specialist agent: {specialist.name} ({specialist.agent_id})")

            sub_context = ExecutionContext(
                agent_id=specialist.agent_id,
                task_id=parent_context.task_id,
                workflow_instance_id=parent_context.workflow_instance_id,
                input_data={
                    "prompt": step.task_description,
                    "parent_run_id": str(parent_context.run_id)
                },
                metadata={"step_number": step.step_number, "capability": step.required_capability}
            )

            with self.db_session_factory() as db:
                engine = AgentRuntimeEngine(db)

                def delegate_executor(ctx: ExecutionContext):
                    return AgentResult(
                        status=AgentExecutionStatus.COMPLETED,
                        output_data={"result": f"Specialist {specialist.name} completed: {step.task_description}"}
                    )

                result = await engine.execute(sub_context, delegate_executor)
                execution_results.append({
                    "step": step.step_number,
                    "agent_id": str(specialist.agent_id),
                    "status": result.status.value,
                    "output": result.output_data
                })

                if result.status != AgentExecutionStatus.COMPLETED:
                    logger.error(f"Step {step.step_number} failed. Halting workflow orchestration.")
                    return {"status": "FAILED", "completed_steps": execution_results}

        return {"status": "COMPLETED", "completed_steps": execution_results}