import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from apps.agent_runtime.graphs.streaming import stream_agent_execution

router = APIRouter(prefix ="agents", tags = ["streaming"])

@router.post("/{run_id}/stream")
async def stream_agent_run(run_id: str, payload: dict):
    initial_state = {
        "run_id": run_id,
        "input_data": payload.get("input_data", {}),
        "messages": [],
        "tool_results": [],
        "status": "RUNNING"
    }

    async def event_generator():
        async for event in stream_agent_execution(initial_state, run_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type= "text/event-stream")