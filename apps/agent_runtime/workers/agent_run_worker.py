import asyncio
from uuid import UUID
from typing import Dict, Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from apps.agent_runtime.application.runtime.context import ExecutionContext
from apps.agent_runtime.application.runtime.engine import AgentRuntimeEngine
from apps.agent_runtime.application.runtime.loop import AgentExecutionLoop
from apps.agent_runtime.application.runtime.mcp_client import ToolServiceMCPClient
from apps.agent_runtime.llm.reasoner import Reasoner
from apps.agent_runtime.domain.agent_contract import AgentResult, AgentExecutionStatus, AgentError
from packages.messaging.nats.event_bus import EventBus
from packages.logging.structured_logs import struc_logger as logger


class AgentRunWorker:
    def __init__(
            self,
            db_session_factory,
            event_bus: EventBus,
            tool_service_url: str,
            llm_model: str = "gpt-4o"):
        self.db_session_factory = db_session_factory
        self.event_bus = event_bus
        self.mcp_client = ToolServiceMCPClient(tool_service_url)

        llm = ChatOpenAI(model=llm_model, temperature=0)
        self.reasoner = Reasoner(llm)

        self.execution_loop = AgentExecutionLoop(
            reasoner=self.reasoner,
            mcp_client=self.mcp_client,
            max_iterations=10,
            max_execution_time_seconds=60.0
        )

    async def start(self) -> None:
        """
        Initializes the event bus connection and registers the listener 
        for incoming agent task requests.
        """
        await self.event_bus.initialize()

        await self.event_bus.register_listener(
            subject="agent.run.requested",
            durable_name="agent-runtime-worker-durable",
            handler=self.handle_agent_run_request
        )
        logger.info("AgentRunWorker successfully registered and listening for tasks.")

    async def handle_agent_run_request(self, raw_payload: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """
        Handler callback matching EventBus/Subscriber signature: 
        handler(raw_payload, metadata)
        """
        logger.info(f"Processing agent run event metadata: {metadata}")

        try:
            agent_id = UUID(raw_payload["agent_id"])
            task_id = UUID(raw_payload["task_id"])
            workflow_instance_id = UUID(raw_payload["workflow_instance_id"])
            input_data = raw_payload.get("input_data", {})
            agent_metadata = raw_payload.get("metadata", {})

            context = ExecutionContext(
                agent_id=agent_id,
                task_id=task_id,
                workflow_instance_id=workflow_instance_id,
                input_data=input_data,
                metadata=agent_metadata
            )

            with self.db_session_factory() as db:
                engine = AgentRuntimeEngine(db)

                def agent_executor(ctx: ExecutionContext) -> AgentResult:
                    initial_messages = [
                        HumanMessage(content=str(ctx.input_data.get("prompt", ctx.input_data)))
                    ]

                    loop_result = asyncio.run(self.execution_loop.run(ctx, initial_messages))

                    if loop_result["status"] == "COMPLETED":
                        return AgentResult(
                            status=AgentExecutionStatus.COMPLETED,
                            output_data={"response": loop_result.get("output")}
                        )
                    else:
                        return AgentResult(
                            status=AgentExecutionStatus.FAILED,
                            error=AgentError(
                                code="LOOP_FAILURE",
                                message=loop_result.get("error", "Unknown execution error"),
                                retryable=True
                            )
                        )

                result = await engine.execute(context, agent_executor)
                logger.info(f"Agent run {context.run_id} finished execution with status: {result.status.value}")

        except Exception as e:
            logger.error(f"Critical error handling agent run request: {str(e)}", exc_info=True)
            raise