import asyncio
import sys
import uuid
from contextlib import asynccontextmanager
from urllib.request import Request

from fastapi import FastAPI
from sqlalchemy.orm.exc import StaleDataError
from starlette.responses import JSONResponse

from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.graphs.agent_graph import AgentGraph
from apps.agent_runtime.infrastructure.agent_runtime_nats_client import agent_nats_client as nats
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client
from apps.agent_runtime.infrastructure.outbox_publisher import agent_outbox_publisher
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.repository.rag_repository import KBRepository
from packages.redis.redis_client import redis_client
from apps.agent_runtime.config.settings import agent_runtime_settings as settings

async def run_end_to_end_graph(prompt: str) -> AgentContext:
    """Executes the agent runtime graph end-to-end mutating AgentContext in place."""
    task_id = str(uuid.uuid4())
    workflow_instance_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    # Ingest the knowledge base to the DB
    with next(db_client.get_session()) as session:
        kb_repo = KBRepository(db= session)
        print("Running automated knowledge base sync")
        ingested = await kb_repo.ingest_kb(settings.KNOWLEDGE_BASE_PATH)
        print(f"✅ [KB Pipeline] Ingested/Updated {len(ingested)} documents.")

    print("\n" + "=" * 65)
    print("🚀 [Agent Runtime] Starting End-to-End Execution with AgentContext")
    print(f"   Task ID:              {task_id}")
    print(f"   Workflow Instance ID: {workflow_instance_id}")
    print(f"   Run ID:               {run_id}")
    print(f"   Prompt:               \"{prompt}\"")
    print("=" * 65 + "\n")

    initial_context = AgentContext(
        task_id=task_id,
        workflow_instance_id=workflow_instance_id,
        run_id=run_id,
        prompt=prompt,
        data={
            "specifications": [
                "Expose /healthz endpoint",
                "Generate production Dockerfile and Kubernetes manifests",
            ],
            "tasks": [],
            "code_artifacts": {},
            "review_comments": [],
            "is_review_approved": False,
            "review_iterations": 0,
            "status": "INITIALIZED",
        },
        agent_configuration={},
    )

    graph = AgentGraph()
    config = {"configurable": {"thread_id": task_id}}

    print("⚡ [Graph Engine] Executing graph nodes...")
    final_result: AgentContext = await graph.ainvoke(initial_context, config=config)
    if isinstance(final_result, dict):
        data = final_result.get("input_data", {})
    else:
        data = getattr(final_result, "input_data", {})
    artifacts = data.get("code_artifacts", {})

    print("\n" + "=" * 65)
    print("✅ [Agent Runtime] Execution Finished Successfully!")
    print(f"   Final Status:    {data.get('status')}")
    print(f"   Review Comments: {data.get('review_comments')}")
    print(f"   GitHub Repo:     {data.get('github_repo_url')}")
    print(f"   Deployment URL:  {data.get('deployment_url')}")
    print(f"   Monitoring URL:  {data.get('monitoring_url')}")
    print(f"   Generated Files: {list(artifacts.keys())}")
    for file_name, code in artifacts.items():
        print(f"\n--- [Artifact: {file_name}] ---")
        preview = code.strip() if len(code) < 300 else code.strip()[:300] + "\n... (truncated)"
        print(preview)
    print("=" * 65 + "\n")

    return final_result


@asynccontextmanager
async def agent_runtime_lifespan(app: FastAPI):
    if not db_client.check_health():
        raise RuntimeError("Workflow database health check failed on startup!")

    await redis_client.initialize()
    await nats.initialize()
    logger.info("NATS Messaging Core successfully initialized.")
    await nats.client.ensure_stream(stream_name="workflow_events", subjects=['workflow.events.task.>'])

    outbox_task = asyncio.create_task(agent_outbox_publisher.start())
    logger.info("Outbox Publisher Worker started successfully.")
    durable_name = "workflow-events-task-ready"
    """
    await nats.register_listener(
        subject="Agent_runtime_initiated",
        durable_name=durable_name,
        handler=task_event_handler,
        stream="workflow_events",
    )
    """
    yield

    agent_outbox_publisher.stop()
    await outbox_task

    await nats.shutdown()
    await redis_client.close()
    logger.info("NATS Messaging Core successfully disconnected.")


app = FastAPI(title="ADD_Platform Agent Runtime Service", lifespan=agent_runtime_lifespan)


@app.exception_handler(StaleDataError)
async def stale_data_exception_handler(request: Request, exc: StaleDataError):
    logger.warning(f"Optimistic lock conflict detected: {exc}")
    return JSONResponse(
        status_code=409,
        content={
            "error": "RESOURCE_CONFLICT",
            "message": "The resource was updated by another request. Please retry your operation.",
        },
    )


if __name__ == "__main__":
    sample_prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "I want a fully functional website/Portfolio for a Photographer named \"JohnDoe\" with a healthcheck and deployment setup"
    )
    asyncio.run(run_end_to_end_graph(sample_prompt))