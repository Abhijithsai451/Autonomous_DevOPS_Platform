from typing import Dict, Any

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.constants import END
from langgraph.graph import StateGraph

from apps.agent_runtime.graphs.state import AgentGraphState
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger

class AgentGraphBuilder:
    def __init(self, mcp_client):
        self.mcp_client = mcp_client

    def build(self) -> StateGraph:
        workflow = StateGraph(AgentGraphState)

        workflow.add_node("reason", self._reason_node)
        workflow.add_node("act", self._act_node)
        workflow.set_entry_point("reason")

        workflow.add_conditional_edges(
            "reason",
            self._should_continue,
            {
                "continue_to_tool": "act",
                "end": END
            }
        )
        workflow.add_edge("act", "reason")

        return workflow.compile()

    async def _reason_node(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Calls the LLM with the current context and message history.
        """
        context = state["context"]
        messages = state["messages"]
        iteration = state.get("iteration_count", 0) + 1

        logger.info(f"Agent run {context.run_id} - Reason iteration {iteration}")

        # Bind MCP tools to LLM (fetched dynamically from the MCP tool service)
        # tools = await self.mcp_client.list_tools()
        # model_with_tools = self.llm.bind_tools(tools)

        # response = await model_with_tools.ainvoke(messages)

        response = AIMessage(content="Thinking or calling tool...")

        return {
            "messages": [response],
            "iteration_count": iteration
        }

    def _should_continue(self, state: AgentGraphState) -> str:
        messages = state["messages"]
        last_message = messages[-1]

        # Check iteration limit safeguards
        if state["iteration_count"] > state.get("max_iterations", 10):
            return "end"

        # If the LLM decided to invoke tool calls, route to 'act'
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue_to_tool"

        return "end"

    async def _act_node(self, state: AgentGraphState) -> Dict[str, Any]:
        """
        Executes tool calls via the remote MCP client.
        """
        messages = state["messages"]
        last_message = messages[-1]
        tool_messages = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            logger.info(f"Executing remote MCP tool: {tool_name}")
            try:
                result = await self.mcp_client.call_tool(tool_name, tool_args)
                tool_messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_call_id)
                )
            except Exception as e:
                logger.error(f"MCP tool execution failed for {tool_name}: {str(e)}")
                tool_messages.append(
                    ToolMessage(content=f"Error executing tool: {str(e)}", tool_call_id=tool_call_id)
                )

        return {"messages": tool_messages}