from apps.agent_runtime.domain.agent_contract import BaseAgent, AgentResult, AgentContext, AgentExecutionStatus, \
    AgentError
from apps.agent_runtime.graphs.base_graph import base_graph, build_base_agent_graph
from apps.agent_runtime.graphs.state import AgentState
from apps.agent_runtime.infrastructure.checkpoint import get_postgres_checkpointer


class LangGraphAgent(BaseAgent):
    """
    Base Agent execution wrapper powered by Langgraph
    """
    def execute(self, context: AgentContext)-> AgentResult:
        initial_state: AgentState = {
            "run_id": str(context.run_id),
            "agent_id": str(context.agent_id),
            "task_id": str(context.task_id),
            "workflow_instance_id": str(context.workflow_instance_id),
            "input_data": context.input_data,
            "output_data": None,
            "error": None,
            "messages": [],
            "tool_results": [],
            "status": AgentExecutionStatus.RUNNING.value,
        }
        config = {
            "configurable": {
                "thread_id": str(context.run_id),
            }
        }
        try:
            with get_postgres_checkpointer() as checkpointer:
                graph = build_base_agent_graph(checkpointer = checkpointer)
                final_state = graph.invoke(initial_state, config = config)

            return AgentResult(
                status = AgentExecutionStatus(final_state["status"]),
                output_data = final_state.get("output_data"),
                error = None
            )
        except Exception as e:
            return AgentResult(
                status=AgentExecutionStatus.FAILED,
                output_data=None,
                error=AgentError(
                    code="LANGGRAPH_EXECUTION_ERROR",
                    message=str(e),
                    retryable=False,
                ),
            )