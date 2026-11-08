from typing import Dict, Any
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.config.settings import agent_runtime_settings as settings
from apps.agent_runtime.llm.prompts import code_orchestrator_prompt
from apps.agent_runtime.llm.prompts.code_orchestrator_prompt import build_qa_prompt


class QAAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-backend-agent", agent_type="backend_agent")
        self.model = llm_model
        self.system_prompt = code_orchestrator_prompt.qa_system_prompt
    async def execute(self,  task, target_files, file_path)-> Dict[str, Any]:
        task_id = task.get("task_id")
        description = task.get("description")
        target_files = task.get("target_files", [])

        logger.info(f"QA Agent: Executing sanity check for task {task_id}")

        sandbox_dir = settings.SANDBOX_DIR
        file_code = {}

        for file_path in target_files:
            full_path = sandbox_dir / file_path
            if full_path.exists():
                file_code[file_path] = full_path.read_text(encoding="utf-8")
            else:
                file_code[file_path] = "[FILE MISSING IN SANDBOX]"

        prompt = build_qa_prompt(task_id, description,target_files, file_code )
        response = await self.model.aexecute(
            message=prompt,
            system_prompt=self.system_prompt,
        )
        return response

    async def qa_node(self, state:AgentContext):
        logger.info("[Node: QA Agent] Starting QA sanity validation on implemented code...")
        data = state.data
        tasks = state.data.get("tasks", [])

        codebase = state.data.get("codebase", {})
        if not codebase:
            logger.warning("[Node: QA Agent] No codebase files found in state to review.")
            return {"data": data}

        if "qa_reports" not in data:
            data["qa_reports"] = {}
        all_passed = True

        for task in tasks:
            current_status = task.get("status")
            logger.info(f"Task status from the state.data.tasks is {current_status} ")
            if current_status in ["VERIFIED", "FINISHED", "PENDING", None]:
                continue

            task_id = task.get("task_id")
            target_files = task.get("target_files", [])
            print(f"target_files location is {str(target_files)}")

            logger.info(f"[Node: QA Agent] Performing sanity check on task {task_id} for files {target_files}...")

            response = await self.execute(task)
            data["qa_reports"][task_id] = response

            if "STATUS: PASS" in response.upper():
                task["status"] = "VERIFIED"
                task["qa_status"] = "VERIFIED"
            else:
                task["status"] = "FAILED"
                task["qa_status"] = "FAILED"
                all_passed = False

        data["code_orchestration_iterations"] = data.get("code_orchestration_iterations", 0) + 1

        if all_passed:
            data["code_orchestration_status"] = "VERIFIED"
        else:
            data["code_orchestration_status"] = "PENDING"

        return {"data": data}