from pathlib import Path
from typing import Dict, Any

from langgraph.types import Send

from apps.agent_runtime.config.settings import agent_runtime_settings as settings
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger


class TestOrchestrator(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        self.integration_test_prompt = None
        self.e2e_test_prompt = None
        self.test_runner_prompt = None

    async def execute(self, prompt, system_prompt)-> Dict[str, Any]:
        logger.info("Agent Prompt Created and Invoking the LLM")
        response = await self.model.aexecute(
            message=prompt,
            system_prompt=system_prompt,
        )
        return response

    async def test_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Test Orchestrator] Initializing pre-production testing phase...")
        if "test_status" not in state.data:
            state.data["test_status"] = "PENDING"
        return state

    async def integration_test_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Integration Test Agent] Generating backend integration test suite...")
        codebase = state.data.get("codebase", {})
        sandbox_dir = settings.SANDBOX_DIR

        code_summary = ""
        for file_path, info in codebase.items():
            abs_path = Path(info.get("absolute_path", sandbox_dir / file_path))
            if abs_path.exists():
                code_summary += f"\n--- FILE: {file_path} ---\n{abs_path.read_text(encoding='utf-8')}\n"

        prompt = f"Generate integration tests for this codebase:\n{code_summary}"
        test_code = await self.execute(prompt, self.integration_test_prompt)


        test_file = sandbox_dir / "src" / "tests" / "integration" / "api.integration.test.ts"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code, encoding="utf-8")
        logger.info(f"[Node: Integration Test Agent] Written to {test_file}")

        return {"data": {**state.data, "integration_test_written": True}}

    async def e2e_test_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: E2E Test Agent] Generating end-to-end test suite...")
        codebase = state.data.get("codebase", {})
        sandbox_dir = settings.SANDBOX_DIR
        code_summary = ""
        for file_path, info in codebase.items():
            abs_path = Path(info.get("absolute_path", sandbox_dir / file_path))
            if abs_path.exists():
                code_summary += f"\n--- FILE: {file_path} ---\n{abs_path.read_text(encoding='utf-8')}\n"

        prompt = f"Generate E2E tests for this codebase:\n{code_summary}"
        test_code = await self.execute(prompt, self.e2e_test_prompt)
        test_file = sandbox_dir / "src" / "tests" / "e2e" / "user_journey.spec.ts"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code, encoding="utf-8")
        logger.info(f"[Node: E2E Test Agent] Written to {test_file}")

        return {"data": {**state.data, "e2e_test_written": True}}
    async def test_runner_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Test Runner Agent] Executing test suite in sandbox terminal...")
        sandbox_dir = settings.SANDBOX_DIR

        try:
            result = subprocess.run(
                ["npm", "test"],  # Or ["pytest"] depending on your stack
                cwd=sandbox_dir,
                capture_output=True,
                text=True,
                timeout=90
            )
            test_output = result.stdout + "\n" + result.stderr
            logger.info(f"[Test Runner] Exit Code: {result.returncode}")

            state.data["test_telemetry"] = {
                "exit_code": result.returncode,
                "output": test_output[:2000]
            }

            if result.returncode == 0:
                state.data["test_status"] = "PASSED"
                logger.info("[Node: Test Runner] All test suites passed successfully!")
            else:
                state.data["test_status"] = "FAILED"
                logger.warning("[Node: Test Runner] Test failures detected. Injecting remediation task.")

                tasks = state.data.get("tasks", [])
                tasks.append({
                    "task_id": f"FIX-TESTS-{len(tasks) + 1}",
                    "description": f"Pre-production test failure remediation:\n{test_output[:1000]}",
                    "target_files": list(state.data.get("codebase", {}).keys())[:2],
                    "layer": "BACKEND",
                    "status": "FAILED"
                })
                state.data["tasks"] = tasks
                state.data["code_orchestration_status"] = "PENDING"

        except Exception as e:
            logger.error(f"[Test Runner Error] Execution failed: {e}")
            state.data["test_status"] = "ERROR"

        return {"data": state.data}

    def _route_after_test_orch(self, state: AgentContext)-> str:
        status = state.data.get("test_status")

        if status == "PASSED":
            logger.info("[TestOrchestrator Router] Tests passed. Routing to Reviewer.")
            return "reviewer"

        if status == "FAILED" or status == "ERROR":
            logger.info("[TestOrchestrator Router] Tests failed. Routing back to Code Orchestrator.")
            return "code_orchestrator"

        logger.info("[TestOrchestrator Router] Fanning out to integration and E2E test generators...")
        return [
            Send("integration_test_agent", state.data),
            Send("e2e_test_agent", state.data)
        ]
