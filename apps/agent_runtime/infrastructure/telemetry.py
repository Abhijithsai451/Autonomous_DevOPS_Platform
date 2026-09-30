from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any

from opentelemetry import context
from opentelemetry.trace import Span, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from packages.telemetry.context.correlation import bind_correlation_context
from packages.telemetry.metrics import metrics_registry
from packages.tracing.spans import start_agent_span
from packages.logging.structured_logs import struc_logger as logger


class AgentObservability:
    @staticmethod
    @contextmanager
    def trace_agent_run(agent_id: str,
                        agent_type: str,
                        tenant_id: Optional[str] = None,
                        workflow_instance_id: Optional[str] = None,
                        agent_run_id: Optional[str] = None,
                        parent_context: Optional[Any] = None,
                    ) -> Generator[Span, None, None]:
        """
        Context manager wrapping an entire agent run:
        Binds context, creates OTel spans, and injects trace keys into structlog.
        """
        token = context.attach(parent_context) if parent_context else None
        try:
            with bind_correlation_context(tenant_id=tenant_id, workflow_instance_id=workflow_instance_id,
                                            agent_run_id=agent_run_id, agent_id=agent_id):
                with start_agent_span(
                                name=f"agent.run.{agent_type}",
                                attributes={
                                    "agent.id": agent_id,
                                    "agent.type": agent_type,
                                    "workflow.instance_id": workflow_instance_id,
                                },
                ) as span:
                    yield span
        finally:
            if token is not None:
                context.detach(token)

    @staticmethod
    def record_metrics(agent_type: str,status: str,duration: float,provider: str = "openai",model: str = "gpt-4o",
                        prompt_tokens: int = 0,completion_tokens: int = 0) -> None:
        """
        Records execution counters, duration histograms, and token usage
        using low-cardinality label rules.
        """

        metrics_registry.record_agent_run(agent_type=agent_type,status=status,duration=duration)

        total_tokens = prompt_tokens + completion_tokens
        if total_tokens > 0:
            metrics_registry.record_llm_call(   provider=provider,
                                                model=model,
                                                status=status,
                                                duration=duration,
                                                tokens=total_tokens,
                                            )

    @staticmethod
    @contextmanager
    def trace_tool_execution(tool_name: str, agent_id: str)-> Generator[Span, None, None]:
        """ Context Manager for nested tool invocation spans."""
        with start_agent_span(
            name=f"agent.tool.{tool_name}",
            attributes = {
                            "tool.name": tool_name,
                            "agent.id": agent_id,
                            "component":"agent_tool",
                        },
        ) as span:
            logger.info("Tool execution started", extra_data = {"tool_name": tool_name})
            try:
                yield span
                span.set_status(StatusCode.OK)
            except Exception as e:
                span.set_status(StatusCode.ERROR, str(e))
                span.record_exception(e)
                logger.error(f"Tool Execution Error in {tool_name} tool execution: {str(e)}")
                raise e

    @staticmethod
    @contextmanager
    def trace_llm_call(provider: str, model: str)-> Generator[Span, None, None]:
        """Context Manager for tracing raw LLM API generations"""
        with start_agent_span(
            name=f"llm.completion.{provider}",
            attributes={
                "llm.provider": provider,
                "llm.model": model,
                "component": "llm_client",
            }
        ) as span:
            yield span

    @staticmethod
    def inject_trace_context(headers: Dict[str, str])-> Dict[str, str]:
        """
        Injects the active OpenTelemetry trace context into an outgoing headers dictionary.
        (eg: for Nats Jetstream metadata/outbox heacers.)
        """
        TraceContextTextMapPropagator().inject(headers)
        return headers

    @staticmethod
    def extract_trace_context(headers: Dict[str, str])-> Any:
        """
        Extracts an incoming OpenTelemetry trace context from message metadata/header
        """
        return TraceContextTextMapPropagator().extract(headers or {})

