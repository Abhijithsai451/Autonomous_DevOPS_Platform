import json
from asyncio import subprocess
from pathlib import Path
from typing import Dict, Any

from langgraph.types import Send
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client
from apps.agent_runtime.config.settings import agent_runtime_settings as settings
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.llm.prompts import test_orchestrator_prompt
from apps.agent_runtime.llm.prompts.test_orchestrator_prompt import build_test_orchestrator_prompt
from apps.agent_runtime.repository.rag_repository import KBRepository


class TestOrchestrator(BaseAgent):
    def __init__(self,llm_model):
        super().__init__(agent_name="system-planner", agent_type="planner")
        self.model = llm_model
        # System Prompts
        self.test_orchestrator_system_prompt = test_orchestrator_prompt.test_orchestrator_system_prompt
        self.integration_system_prompt = test_orchestrator_prompt.integration_system_prompt
        self.e2e_system_prompt = test_orchestrator_prompt.e2e_system_prompt
        self.runner_system_prompt = test_orchestrator_prompt.runner_system_prompt

        # User Prompts
        self.integration_test_prompt = test_orchestrator_prompt.integration_prompt
        self.e2e_test_prompt = test_orchestrator_prompt.e2e_prompt
        self.test_runner_prompt = test_orchestrator_prompt.runner_prompt

    async def execute(self, prompt, system_prompt)-> Dict[str, Any]:
        logger.info("Agent Prompt Created and Invoking the LLM")
        response = await self.model.aexecute(
            message=prompt,
            system_prompt=system_prompt,
        )
        return response

    async def test_orchestrator_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Test Orchestrator] Analyzing codebase and planning test tasks...")
        data = state.data
        sandbox_dir = settings.SANDBOX_DIR
        iterations = data.get("test_orchestration_iterations", 0) + 1
        data["test_orchestration_iterations"] = iterations

        if iterations > 3:
            logger.warning("[Test Orchestrator] Max test retry limit (3) reached. Bypassing loop to reviewer.")
            data["test_status"] = "MAX_RETRIES_EXCEEDED"
            return {"data": data}

        codebase = data.get("codebase", {})
        code_summary = ""
        for file_path, info in codebase.items():
            abs_path = Path(info.get("absolute_path", sandbox_dir / file_path))
            if abs_path.exists():
                code_summary += f"\n--- FILE: {file_path} ---\n{abs_path.read_text(encoding='utf-8')}\n"
        try:
            rag_query = "website requirements, feature catalog, quality standards, accessibility, and testing acceptance criteria"
            with next(db_client.get_session()) as session:
                repo = KBRepository(db=session)
                context = await repo.retrieve_context(rag_query, 3)
        except Exception as ex:
            logger.warning(f"Task Orchestrator: Failed to retrieve RAG context: {ex}")
        prompt_payload = build_test_orchestrator_prompt(code_summary, context)
        raw_response = await self.execute(
            message=prompt_payload["message"],
            system_prompt=self.system_prompt
        )
        try:
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1]
                if cleaned_response.startswith("json"):
                    cleaned_response = cleaned_response[4:].strip()

            test_tasks = json.loads(cleaned_response)
        except Exception as e:
            logger.error(f"[Test Orchestrator Error] Failed to parse JSON test tasks: {e}. Raw: {raw_response}")
            test_tasks = [
                {
                    "task_id": "TEST-INT-01",
                    "layer": "INTEGRATION",
                    "target_files": ["src/tests/integration/api.integration.test.ts"],
                    "description": "Fallback integration test suite for core routes.",
                    "status": "PENDING"
                },
                {
                    "task_id": "TEST-E2E-01",
                    "layer": "E2E",
                    "target_files": ["src/tests/e2e/user_journey.spec.ts"],
                    "description": "Fallback E2E user journey test suite.",
                    "status": "PENDING"
                }
            ]

        data["test_tasks"] = test_tasks
        data["test_status"] = "PENDING"
        logger.info(f"[Node: Test Orchestrator] Successfully planned {len(test_tasks)} test tasks.")

        return {"data": data}

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
                ["npm", "test"],
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
