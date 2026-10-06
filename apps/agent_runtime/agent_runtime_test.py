import warnings
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import text

from apps.agent_runtime.agent_runtime_main import app
from apps.agent_runtime.domain.agent_contract import AgentContext, AgentExecutionStatus, AgentResult, AgentError
from apps.agent_runtime.domain.outbox import OutboxStatus, OutboxEvent
from apps.agent_runtime.graphs.nodes import analyze_node
from apps.agent_runtime.graphs.router import should_continue
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client, agent_db_session
from apps.agent_runtime.infrastructure.outbox_publisher import agent_outbox_publisher
from apps.agent_runtime.infrastructure.telemetry import AgentObservability
from apps.agent_runtime.llm.factory import get_llm_model
from packages.auth.auth_jwt import get_current_user

warnings.filterwarnings("ignore", category = DeprecationWarning, module = "starlette")
DATA = {}
MOCK_USER = {"id": "test-user-id", "email": "test@example.com","role": "admin"}


@pytest.fixture(autouse = True)
def override_auth_dependency():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function", autouse = True)
def db_session():
    """
    Provides a rollback-isolation database connection and populates shared DATA
    """
    connection = db_client.engine.connect()
    transaction = connection.begin()
    session = db_client.SessionLocal(bind=connection)

    agent = session.execute( text("SELECT id FROM agent_runtime.agents LIMIT 1")).fetchone()
    if agent:
        DATA["agent_id"] = str(agent[0])
    run = session.execute(text("SELECT id FROM agent_runtime.agent_runs LIMIT 1")).fetchone()

    if run:
        DATA["run_id"] = str(run[0])

    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest_asyncio.fixture
async def client():
    headers = {"Authorization": f"Bearer {MOCK_USER}"}
    transport = ASGITransport(app=app)
    async with AsyncClient( transport = transport, base_url="http://test", headers=headers) as ac:
        async with app.router.lifespan_context(app):
            yield ac


def test_agent_context_instantiation():
    task_id = uuid4()
    workflow_instance_id = uuid4()
    agent_id = uuid4()

    ctx = AgentContext(task_id=task_id,
                       workflow_instance_id=workflow_instance_id,
                       run_id=str(uuid4()),
                       configuration={"model": "gpt-4o"},
                       agent_id=agent_id,
                       input_data = {"query":"check node health"},)

    assert ctx.task_id == task_id
    assert ctx.workflow_instance_id == workflow_instance_id
    assert ctx.task_id == task_id
    assert ctx.workflow_instance_id == workflow_instance_id

def test_agent_result():
    run_id = uuid4()
    result = AgentResult(status = AgentExecutionStatus.COMPLETED,
                         output_data = {"status", "healthy"},
                         )
    assert result.status == AgentExecutionStatus.COMPLETED

    err = AgentError(code="EXECUTION_TIMEOUT", message="Tool execution timed out")
    failed_result = AgentResult( status = AgentExecutionStatus.FAILED,
                                error = err)

    assert failed_result.status == AgentExecutionStatus.FAILED
    assert failed_result.error.code  == "EXECUTION_TIMEOUT"

def test_telemetry_trace_context():
    headers = {}
    injected = AgentObservability.inject_trace_context(headers)
    assert isinstance(injected, dict)


@pytest.mark.anyio
async def test_create_agent_run(client):
    payload = {
        "agent_id": DATA.get("agent_id", str(uuid4())),
        "task_id": str(uuid4()),
        "workflow_instance_id": str(uuid4()),
        "input_data": {"prompt": "Run diagnostic check"},
    }
    response = await client.post("/agent-runs", json=payload)
    assert response.status_code in [200, 201, 404]


@pytest.mark.anyio
async def test_get_agent_run(client):
    target_id = DATA.get("run_id", str(uuid4()))
    response = await client.get(f"/agent-runs/{target_id}")
    assert response.status_code in [200, 404]


@pytest.mark.anyio
async def test_cancel_agent_run(client):
    target_id = DATA.get("run_id", str(uuid4()))
    response = await client.post(
        f"/agent-runs/{target_id}/cancel", json={"reason": "User requested cancel"}
    )
    assert response.status_code in [200, 400, 404]


# ========================================================
# INTEGRATION TESTS
# ========================================================
@pytest.mark.anyio
def test_outbox_concurrency_skip_locked(db_session):
    event_1_id = uuid4()
    event_2_id = uuid4()

    db_session.execute(
        text("""
             INSERT INTO agent_runtime.outbox_events (id, event_type, aggregate_type, aggregate_id, payload, status)
             VALUES (:e1, 'agent_runtime.events.Test1', 'AgentRun', :a1, '{}', 'PENDING'),
                    (:e2, 'agent_runtime.events.Test2', 'AgentRun', :a2, '{}', 'PENDING')
             """),
        {"e1": event_1_id, "e2": event_2_id, "a1": uuid4(), "a2": uuid4()},
    )
    db_session.commit()

    selected_events = db_session.execute(
        text(
            "SELECT id FROM agent_runtime.outbox_events WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED"
        )
    ).fetchall()

    assert len(selected_events) >= 2


@pytest.mark.asyncio
async def test_outbox_publisher_e2e(monkeypatch):
    mock_publish = AsyncMock(return_value=None)
    monkeypatch.setattr(agent_outbox_publisher.bus, "publish", mock_publish)

    event_id = str(uuid4())
    run_id = uuid4()
    event_type = "agent_runtime.events.agent_run.completed"
    payload = {
        "event_id": event_id,
        "run_id": str(run_id),
        "task_id": str(uuid4()),
        "workflow_instance_id": str(uuid4()),
        "status": "COMPLETED",
        "output": {"result": "success"},
    }

    db = next(agent_db_session())
    outbox_entry = OutboxEvent(
        id=event_id,
        aggregate_type="AGENT_RUN",
        aggregate_id=run_id,
        event_type=event_type,
        payload=payload,
        status=OutboxStatus.PENDING,
    )
    db.add(outbox_entry)
    db.commit()

    processed_count = await agent_outbox_publisher.process_events()

    assert processed_count == 1
    mock_publish.assert_called_once_with(
        event_type=event_type, payload=payload
    )

    db.refresh(outbox_entry)
    assert outbox_entry.status == OutboxStatus.PUBLISHED