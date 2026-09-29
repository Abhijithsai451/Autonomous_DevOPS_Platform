from typing import Dict, Any, AsyncGenerator

from apps.agent_runtime.graphs.base_graph import build_base_agent_graph
from apps.agent_runtime.infrastructure.checkpoint import get_postgres_checkpointer


async def stream_agent_execution(initial_state: Dict[str, Any], run_id: str)-> AsyncGenerator[Dict[str, Any]]:
    """
    Streams execution events (LLM Tokens, tool calls, state changes) in real time
    """
    config = {"configurable": {"thread_id": str(run_id)}}

    with get_postgres_checkpointer() as checkpointer:
        graph = build_base_agent_graph(checkpointer = checkpointer)

        async for event in graph.astream_events(initial_state, config = config, version="v2"):
            event_type = event["event"]

            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.event:
                    yield {
                        "event": "token",
                        "data": {"content": chunk.content, "run_id": run_id}
                    }
            elif event_type in ("on_chain_start", "on_chain_end"):
                node_name = event["name"]
                if node_name in ["analyze","llm","format","tools"]:
                    yield {
                        "event": f"node_{event_type.split('_')[-1]}",
                        "data": {"node": node_name, "run_id": run_id}
                    }
            elif event_type == "on_tool_end":
                yield {
                    "event": "tool_completed",
                    "data": {
                        "tool": event["name"],
                        "output": str(event["data"].get("output")),
                        "run_id": run_id
                    }
                }