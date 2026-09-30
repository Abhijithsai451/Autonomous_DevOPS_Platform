import uuid
import pytest
import asyncio
from httpx import ASGITransport, AsyncClient

from apps.tool_gateway.domain.tool_definition import ToolDefinition, ToolStatus
from apps.tool_gateway.domain.tool_execution_request import ToolExecutionRequest
from apps.tool_gateway.domain.tool_execution_result import ToolExecutionStatus
from apps.tool_gateway.tool_gateway_main import app, register_default_tools
from apps.tool_gateway.tools.base import BaseTool
from apps.tool_gateway.tools.json_transform import JsonTransformTool
from packages.auth.auth_jwt import get_current_user

from apps.tool_gateway.application.registry import ToolRegistry, tool_registry
from apps.tool_gateway.application.executor import ToolExecutionEngine
from apps.tool_gateway.infrastructure.opa_client import AuthorizationEngine
from apps.tool_gateway.tools.echo import EchoTool

MOCK_USER = {"id": "test-user-id", "email": "test@example.com", "role": "admin"}

@pytest.fixture(autouse=True)
def setup_auth_and_registry():
    """Overrides auth dependency and registers tools into global registry."""
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    # Re-register tools to ensure fresh instance per test
    tool_registry.register(EchoTool())
    tool_registry.register(JsonTransformTool())

    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    headers = {"Authorization": f"Bearer {MOCK_USER}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=headers
    ) as ac:
        yield ac


# ========================================================
# UNIT TESTS
# ========================================================

@pytest.mark.anyio
async def test_unit_tool_registry_registration():
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo)

    retrieved = registry.get_tool("echo")
    assert retrieved is not None
    assert retrieved.definition.slug == "echo"


@pytest.mark.anyio
async def test_unit_authorization_engine():
    auth = AuthorizationEngine()

    # Authorized Request
    valid_req = ToolExecutionRequest(
        execution_id="unit-1",
        organization_id="org_test",
        agent_id="agent_01",
        tool_slug="echo",
    )
    assert await auth.is_authorized(valid_req) is True

    # Unauthorized Request (Missing org_id)
    invalid_req = ToolExecutionRequest(
        execution_id="unit-2",
        organization_id="",
        agent_id="agent_01",
        tool_slug="echo",
    )
    assert await auth.is_authorized(invalid_req) is False


@pytest.mark.anyio
async def test_unit_executor_timeout():
    class SlowTool(BaseTool):
        @property
        def definition(self) -> ToolDefinition:
            return ToolDefinition(
                id="slow_v1",
                name="Slow Tool",
                slug="slow_tool",
                description="Simulates slow execution",
                version="1.0.0",
                status=ToolStatus.ACTIVE,
                input_schema={"type": "object", "properties": {}},
            )

        async def run(self, input_data):
            try:
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                # Re-raise CancelledError so asyncio.timeout / asyncio.wait_for works properly
                raise
            return {"status": "done"}

    registry = ToolRegistry()
    registry.register(SlowTool())
    engine = ToolExecutionEngine(registry)

    req = ToolExecutionRequest(
        execution_id="unit-timeout",
        organization_id="org_test",
        agent_id="agent_01",
        tool_slug="slow_tool",
        input_data={},
        timeout_seconds=1,
    )

    result = await engine.execute(req)
    # Check if timeout occurred
    assert result.status in [ToolExecutionStatus.TIMEOUT, ToolExecutionStatus.FAILED]
    if result.status == ToolExecutionStatus.TIMEOUT:
        assert "timed out" in result.error_message.lower()


# ========================================================
# INTEGRATION / API TESTS
# ========================================================

@pytest.mark.anyio
async def test_api_healthz(client):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "tool-gateway"}


@pytest.mark.anyio
async def test_api_execute_echo_success(client):
    payload = {
        "execution_id": f"exec-{uuid.uuid4().hex[:6]}",
        "organization_id": "cortexops_main",
        "agent_id": "agent_test_01",
        "tool_slug": "echo",
        "input_data": {"message": "Hello CortexOps!"},
    }
    response = await client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Print error details if status isn't success for debugging
    assert data.get("status") == "success", f"Execution failed with error: {data.get('error_message')}"
    assert data["output"]["echo"] == "Hello CortexOps!"


@pytest.mark.anyio
async def test_api_execute_json_transform_success(client):
    payload = {
        "execution_id": f"exec-{uuid.uuid4().hex[:6]}",
        "organization_id": "cortexops_main",
        "agent_id": "agent_test_01",
        "tool_slug": "json_transform",
        "input_data": {
            "payload": {"env": "prod", "debug": False, "secret": "1234"},
            "keys": ["env", "debug"],
        },
    }
    response = await client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "success", f"Execution failed with error: {data.get('error_message')}"
    assert data["output"]["result"] == {"env": "prod", "debug": False}


@pytest.mark.anyio
async def test_api_execute_invalid_schema(client):
    payload = {
        "execution_id": f"exec-{uuid.uuid4().hex[:6]}",
        "organization_id": "cortexops_main",
        "agent_id": "agent_test_01",
        "tool_slug": "echo",
        "input_data": {},  # Missing required 'message' key
    }
    response = await client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["invalid_input", "failed"]


@pytest.mark.anyio
async def test_api_execute_unauthorized(client):
    payload = {
        "execution_id": f"exec-{uuid.uuid4().hex[:6]}",
        "organization_id": "",  # Empty org ID
        "agent_id": "agent_test_01",
        "tool_slug": "echo",
        "input_data": {"message": "Blocked"},
    }
    response = await client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unauthorized"


@pytest.mark.anyio
async def test_api_execute_not_found(client):
    payload = {
        "execution_id": f"exec-{uuid.uuid4().hex[:6]}",
        "organization_id": "cortexops_main",
        "agent_id": "agent_test_01",
        "tool_slug": "unknown_tool",
        "input_data": {},
    }
    response = await client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_found"