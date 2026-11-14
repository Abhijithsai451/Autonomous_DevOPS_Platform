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
from apps.agent_runtime.llm.prompts.test_orchestrator_prompt import build_test_orchestrator_prompt, \
    build_integration_test_prompt, build_e2e_test_prompt
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

    def _extract_code_from_markdown(self, text: str) -> str:
        """Safely extracts raw code from markdown code blocks if wrapped by the LLM."""
        text = text.strip()
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                code_block = parts[1]
                newline = code_block.find("\n")
                if newline != -1 and len(code_block[:newline].strip()) < 15:
                    return code_block[newline + 1:].strip()
                return code_block.strip()
        return text
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
            message=prompt_payload,
            system_prompt=self.test_orchestrator_system_prompt
        )
        try:
            response = self._extract_code_from_markdown(raw_response)
            test_tasks = json.loads(response)
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
        data = state.data

        test_tasks = data.get("test_tasks", [])
        integration_tasks = [
            t for t in test_tasks
            if t.get("layer") == "INTEGRATION" and t.get("status") in ["PENDING", "FAILED"]
        ]

        if not integration_tasks:
            logger.info("[Node: Integration Test Agent] No pending integration test tasks found.")
            return {"data": data}

        sandbox_dir = settings.SANDBOX_DIR
        try:
            sandbox_dir.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass
        if "codebase" not in data:
            data["codebase"] = {}

        code_summary = ""
        for file_path, info in data.get("codebase", {}).items():
            abs_path = Path(info.get("absolute_path", sandbox_dir / file_path))
            if abs_path.exists():
                code_summary += f"\n--- FILE: {file_path} ---\n{abs_path.read_text(encoding='utf-8')}\n"

        for task in integration_tasks:
            task_id = task.get("task_id")
            target_files = task.get("target_files", [])
            description = task.get("description", "")

            logger.info(f"[Node: Integration Test Agent] Implementing task {task_id} for files {target_files}...")

            context = ""
            try:
                with next(db_client.get_session()) as session:
                    repo = KBRepository(db=session)
                    rag_query = "integration testing standards backend api testing mock database contracts"
                    context = await repo.retrieve_context(rag_query, 3)
            except Exception as ex:
                logger.warning(f"Integration Test Agent: Failed to retrieve RAG context: {ex}")

            prompt = build_integration_test_prompt(description, code_summary, context)

            response = await self.execute(message=prompt, system_prompt=self.integration_system_prompt)
            clean_code = self._extract_code_from_markdown(response)

            for file_path in target_files:
                full_path = sandbox_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(clean_code, encoding="utf-8")
                logger.info(f"[Node: Integration Test Agent] Integration test file added to {str(full_path)}")

                data["codebase"][file_path] = {
                    "absolute_path": str(full_path),
                    "task_id": task_id
                }

            task["status"] = "FINISHED"
            for t in test_tasks:
                if t.get("task_id") == task_id:
                    t["status"] = "FINISHED"

        logger.info("[Node: Integration Test Agent] All integration test tasks are implemented.")
        return {
            "data": {
                **data,
                "test_tasks": test_tasks,
                "codebase": data["codebase"],
                "agent_audit_trail": {**data.get("agent_audit_trail", {}),
                                      "integration_test_agent": {"status": "COMPLETED"}}
            }
        }

    async def e2e_test_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: E2E Test Agent] Generating end-to-end test suite...")
        data = state.data

        test_tasks = data.get("test_tasks", [])
        integration_tasks = [
            t for t in test_tasks
            if t.get("layer") == "E2E" and t.get("status") in ["PENDING", "FAILED"]
        ]

        if not integration_tasks:
            logger.info("[Node: E2E Test Agent] No pending integration test tasks found.")
            return {"data": data}

        sandbox_dir = settings.SANDBOX_DIR
        try:
            sandbox_dir.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            pass
        if "codebase" not in data:
            data["codebase"] = {}

        code_summary = ""
        for file_path, info in data.get("codebase", {}).items():
            abs_path = Path(info.get("absolute_path", sandbox_dir / file_path))
            if abs_path.exists():
                code_summary += f"\n--- FILE: {file_path} ---\n{abs_path.read_text(encoding='utf-8')}\n"

        for task in integration_tasks:
            task_id = task.get("task_id")
            target_files = task.get("target_files", [])
            description = task.get("description", "")

            logger.info(f"[Node: E2E Test Agent] Implementing task {task_id} for files {target_files}...")

            context = ""
            try:
                with next(db_client.get_session()) as session:
                    repo = KBRepository(db=session)
                    rag_query = "E2E testing standards backend api testing mock database contracts"
                    context = await repo.retrieve_context(rag_query, 3)
            except Exception as ex:
                logger.warning(f"E2E Test Agent: Failed to retrieve RAG context: {ex}")

            prompt = build_e2e_test_prompt(description, code_summary, context)

            response = await self.execute(message=prompt, system_prompt=self.e2e_system_prompt)
            clean_code = self._extract_code_from_markdown(response)

            for file_path in target_files:
                full_path = sandbox_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(clean_code, encoding="utf-8")
                logger.info(f"[Node: E2E Test Agent] Integration test file added to {str(full_path)}")

                data["codebase"][file_path] = {
                    "absolute_path": str(full_path),
                    "task_id": task_id
                }

            task["status"] = "FINISHED"
            for t in test_tasks:
                if t.get("task_id") == task_id:
                    t["status"] = "FINISHED"

        logger.info("[Node: E2E Test Agent] All integration test tasks are implemented.")
        return {
            "data": {
                **data,
                "test_tasks": test_tasks,
                "codebase": data["codebase"],
                "agent_audit_trail": {**data.get("agent_audit_trail", {}),
                                      "e2e_test_agent": {"status": "COMPLETED"}}
            }
        }

    async def test_runner_node(self, state: AgentContext) -> AgentContext:
        logger.info("[Node: Test Runner Agent] Executing test suite in sandbox terminal...")


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
