from pathlib import Path
from typing import Dict, Any
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client
from apps.agent_runtime.llm.prompts import code_orchestrator_prompt
from apps.agent_runtime.llm.prompts.code_orchestrator_prompt import builder_coder_prompt
from apps.agent_runtime.repository.rag_repository import KBRepository
from apps.agent_runtime.config.settings import agent_runtime_settings as settings


class BackendAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-backend-agent", agent_type="backend_agent")
        self.model = llm_model
        self.system_prompt = code_orchestrator_prompt.backend_system_prompt

    async def execute(self,task_id, task,target_files)-> Dict[str, Any]:
        logger.info(f"Backend Agent: Implementing the task {task_id}")
        context = ""
        try:
            with next(db_client.get_session()) as session:
                repo = KBRepository(db=session)
                context = await repo.retrieve_context(task, 5)
        except Exception as ex:
            logger.warning(f"Backend Agent: Failed to retrieve RAG context: {ex}")
        prompt = builder_coder_prompt(context,task, target_files)
        response = await self.model.aexecute(
            message=prompt,
            system_prompt=self.system_prompt,
        )

        return response

    async def backend_node(self, state:AgentContext):
        logger.info("[Node: Backend Agent] Starting backend task implementation...")

        backend_tasks = state.data.get("backend_tasks", [])
        if not backend_tasks:
            logger.warning("[Node: Backend Agent] No backend tasks found in state.")
            return state

        if "codebase" not in state.data:
            state.data["codebase"] = {}
        sandbox_dir = settings.SANDBOX_DIR
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        for task in backend_tasks:
            if task.get("status") == "FINISHED":
                continue

            task_id = task.get("task_id")
            target_files = task.get("target_files")
            description = task.get("description", "")

            logger.info(f"[Node: Backend Agent] Implementing task {task_id}...")
            project_task = f"Implement the following task strictly for files {target_files}:\n{description}"
            response = await self.execute(task_id, project_task, target_files)

            for file_path in target_files:
                full_path = sandbox_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(response, encoding="utf-8")
                logger.info(f"[Node: Backend Agent] file successfully added to the path {str(full_path)}")

                state.data["codebase"][file_path] = {
                    "absolute_path": str(full_path),
                    "task_id": task_id
                }
            task["status"] = "FINISHED"

        return state