import time
from typing import List, Any, Dict
from uuid import UUID

from langchain_core.messages import BaseMessage, AIMessage, ToolMessage

from apps.agent_runtime.application.engine.context import ExecutionContext
from apps.agent_runtime.application.engine.engine import AgentRuntimeEngine
from apps.agent_runtime.domain.actions import AgentDecision, ActionType
from apps.agent_runtime.domain.agent_contract import AgentExecutionStatus, AgentResult
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.llm.reasoner import Reasoner


class AgentExecutionLoop:
    def __init__(self, reasoner: Reasoner,mcp_client,db_session_factory, max_iterations: int = 10, max_execution_time_seconds: float = 60.0):
        self.reasoner = reasoner.decide
        self.mcp_client = mcp_client,
        self.max_iterations = max_iterations,
        self.db_session_factory = db_session_factory
        self.max_execution_time_seconds = max_execution_time_seconds

    async def run(self, context: ExecutionContext, initial_messages: List[BaseMessage]) -> Dict[str, Any]:
        """
        Executes the controlled ReAct loop, validating decisions and orchestrating
        both tools (MCP) and multi-agent delegations (CALL_AGENT) dynamically.
        """
        start_time = time.perf_counter()
        iteration = 0
        messages = list(initial_messages)
        observations: List[str] = []
        current_plan: Dict[str, Any] = {}

        available_tools = await self.mcp_client.list_tools()

        while iteration < self.max_iterations:
            elapsed = time.perf_counter() - start_time
            if elapsed > self.max_execution_time_seconds:
                logger.error(f"Agent run {context.run_id} exceeded max execution time ({self.max_execution_time_seconds}s)")
                return {"status": "FAILED", "error": "Execution timeout exceeded"}

            iteration += 1
            logger.info(f"Run {context.run_id} - Iteration {iteration}/{self.max_iterations}")
            try:
                decision: AgentDecision = await self.reasoner(context=context,messages=messages,available_tools=available_tools,
                                                              current_plan=current_plan,previous_observations=observations)
            except Exception as e:
                logger.exception(f"Reasoner failure: {str(e)}")
                return {"status": "FAILED", "error": f"Reasoner error: {str(e)}"}

            messages.append(AIMessage(content=f"Thought: {decision.thought} [Action: {decision.action_type}]"))

            if decision.action_type == ActionType.FINAL_RESPONSE:
                return {"status": "COMPLETED",
                        "output": decision.action_payload.get("response"),
                        "messages": messages
                        }
            elif decision.action_type == ActionType.CALL_TOOL:
                tool_name = decision.action_payload.get("tool_name")
                tool_args = decision.action_payload.get("arguments", {})

                logger.info(f"Runtime authorized tool call -> {tool_name}")
                try:
                    obs = await self.mcp_client.call_tool(tool_name, tool_args)
                    observations.append(f"Tool {tool_name} returned: {obs}")
                    messages.append(ToolMessage(content=str(obs), tool_call_id=f"call_{iteration}"))
                except Exception as tool_err:
                    err_msg = f"Tool execution error: {str(tool_err)}"
                    logger.error(err_msg)
                    observations.append(err_msg)
                    messages.append(ToolMessage(content=err_msg, tool_call_id=f"call_{iteration}"))

            elif decision.action_type == ActionType.CALL_AGENT:
                target_capability = decision.action_payload.get("capability")
                target_agent_id = decision.action_payload.get("agent_id")
                delegation_prompt = decision.action_payload.get("prompt")

                logger.info(f"Runtime intercepted CALL_AGENT. Capability: {target_capability}, ID: {target_agent_id}")
                try:
                    specialist = None
                    if target_agent_id:
                        specialist = self.agent_repository.get_by_id(UUID(target_agent_id))
                    elif target_capability:
                        matches = self.agent_repository.find_by_capability(target_capability)
                        specialist = matches[0] if matches else None

                    if not specialist or not specialist.is_active:
                        raise RuntimeError(
                            f"No active specialist agent found for capability '{target_capability}' or ID '{target_agent_id}'")

                    sub_context = ExecutionContext(
                        agent_id=specialist.agent_id,
                        task_id=context.task_id,
                        workflow_instance_id=context.workflow_instance_id,
                        input_data={"prompt": delegation_prompt},
                        metadata={"parent_run_id": str(context.run_id)}
                    )
                    with self.db_session_factory() as db:
                        sub_engine = AgentRuntimeEngine(db)

                        def sub_agent_executor(sub_ctx: ExecutionContext) -> AgentResult:
                            return AgentResult(
                                status=AgentExecutionStatus.COMPLETED,
                                output_data={
                                    "response": f"Specialist agent '{specialist.name}' completed task successfully."}
                            )

                        sub_result = await sub_engine.execute(sub_context, sub_agent_executor)

                        if sub_result.status == AgentExecutionStatus.COMPLETED:
                            agent_output = sub_result.output_data.get("response", "Delegated execution completed.")
                            observations.append(f"Agent {specialist.name} returned: {agent_output}")
                            messages.append(
                                ToolMessage(content=str(agent_output), tool_call_id=f"agent_call_{iteration}"))
                        else:
                            err_msg = f"Delegated agent {specialist.name} failed: {sub_result.error}"
                            logger.error(err_msg)
                            observations.append(err_msg)
                            messages.append(ToolMessage(content=err_msg, tool_call_id=f"agent_call_{iteration}"))

                except Exception as delegation_err:
                    err_msg = f"Agent delegation failed: {str(delegation_err)}"
                    logger.error(err_msg)
                    observations.append(err_msg)
                    messages.append(ToolMessage(content=err_msg, tool_call_id=f"agent_call_{iteration}"))

            elif decision.action_type == ActionType.CREATE_PLAN:
                current_plan = decision.action_payload.get("plan", {})
                observations.append(f"Plan updated: {current_plan}")

            elif decision.action_type in (ActionType.WAIT, ActionType.REQUEST_APPROVAL):
                return {
                    "status": "SUSPENDED",
                    "reason": decision.action_type.value,
                    "payload": decision.action_payload
                }

            else:
                logger.warning(f"Unhandled action type received: {decision.action_type}")

        return {"status": "FAILED", "error": "Max iterations reached without completion"}