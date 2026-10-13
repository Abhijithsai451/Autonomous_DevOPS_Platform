import time
from typing import List, Any, Dict

from langchain_core.messages import BaseMessage, AIMessage, ToolMessage

from apps.agent_runtime.application.runtime.context import ExecutionContext
from apps.agent_runtime.domain.actions import AgentDecision, ActionType
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.llm.reasoner import Reasoner


class AgentExecutionLoop:
    def __init__(self, reasoner: Reasoner,mcp_client, max_iterations: int = 10, max_execution_time_seconds: float = 60.0):
        self.reasoner = reasoner
        self.mcp_client = mcp_client,
        self.max_iterations = max_iterations,
        self.max_execution_time_seconds = max_execution_time_seconds

    async def run(self, context: ExecutionContext, initial_messages: List[BaseMessage])-> Dict[str, Any]:
        """
        Executes the controlled React Loop with strict iteration and time safeguards.
        """
        start_time = time.perf_counter()
        iteration = 0
        messages = list(initial_messages)
        observations = list[str]= []
        current_plan = Dict[str, Any] = {}

        available_tools = await self.mcp_client.list_tools()

        while iteration < self.max_iterations:
            elapsed = time.perf_counter() - start_time
            if elapsed > self.max_execution_time_seconds:
                logger.error(f"Agent run {context.run_id} exceeded max time {self.max_execution_time_seconds} seconds. ")
                return {"status": "FAILED", "error": "Execution timeout seconds"}
            iteration +=1
            logger.info(f"Run {context.run_id} - Iteration {iteration}/{self.max_iterations}")

            try:
                decision: AgentDecision = await self.reasoner(context=context, messages = messages,
                                                              available_tools= available_tools, current_plan= current_plan,
                                                              previous_observations = observations)
            except Exception as e:
                logger.exception(f"Reasoner failure: {str(e)}")
                return {"status": "FAILED", "error": f"Reasoner error: {str(e)}"}
            messages.append(AIMessage(content=f"Thought: {decision.thought} [Action: {decision.action_type}]"))

            if decision.action_type == ActionType.FINAL_RESPONSE:
                return {
                    "status": "COMPLETED",
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
            elif decision.action_type == ActionType.CREATE_PLAN:
                current_plan = decision.action_payload.get("plan", {})
                observations.append(f"Plan updated: {current_plan}")

            elif decision.action_type == ActionType.WAIT or decision.action_type == ActionType.REQUEST_APPROVAL:
                return {
                    "status": "SUSPENDED",
                    "reason": decision.action_type.value,
                    "payload": decision.action_payload
                }
            else:
                logger.warning(f"Unhandled action type received: {decision.action_type}")
            return {"status": "FAILED", "error": "Max iterations reached without completion"}