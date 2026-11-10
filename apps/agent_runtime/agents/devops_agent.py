from typing import Dict, Any
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.agents.base_agent import BaseAgent
from apps.agent_runtime.domain.agent_contract import AgentContext
from apps.agent_runtime.config.settings import agent_runtime_settings as settings
from apps.agent_runtime.llm.prompts import code_orchestrator_prompt
from apps.agent_runtime.infrastructure.database import agent_runtime_db_client as db_client
from apps.agent_runtime.llm.prompts.code_orchestrator_prompt import builder_coder_prompt
from apps.agent_runtime.repository.rag_repository import KBRepository


class DevopsAgent(BaseAgent):
    def __init__(self, llm_model):
        super().__init__(agent_name="code-devops-agent", agent_type="devops_agent")
        self.model = llm_model
        self.system_prompt = code_orchestrator_prompt.frontend_system_prompt

    async def execute(self, task_id, task, target_files) -> Dict[str, Any]:
        logger.info(f"DevOps Agent: Implementing the task {task_id}")
        context = ""
        try:
            with next(db_client.get_session()) as session:
                repo = KBRepository(db=session)
                context = await repo.retrieve_context(task, 3)
        except Exception as ex:
            logger.warning(f"DevOps Agent: Failed to retrieve RAG context: {ex}")
        prompt = builder_coder_prompt(context, task, target_files)
        response = await self.model.aexecute(
            message=prompt,
            system_prompt=self.system_prompt,
        )
        return response

    async def devops_node(self, state:AgentContext):
        logger.info("[Node: DevOps Agent] Starting DevOps task implementation...")
        tasks = state.data.get("tasks", [])
        devops_tasks = state.data.get("devops_tasks", [])
        if not devops_tasks:
            logger.warning("[Node: DevOps Agent] No DevOps tasks found in state.")
            return {"data": state.data}

        if "codebase" not in state.data:
            state.data["codebase"] = {}
        sandbox_dir = settings.SANDBOX_DIR
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        for task in devops_tasks:
            if task.get("status") == "FINISHED":
                continue

            task_id = task.get("task_id")
            target_files = task.get("target_files")
            description = task.get("description", "")

            logger.info(f"[Node: DevOps Agent] Implementing task {task_id}...")
            project_task = f"Implement the following task strictly for files {target_files}:\n{description}"
            response = await self.execute(task_id, project_task, target_files)

            for file_path in target_files:
                try:
                    full_path = sandbox_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(response, encoding="utf-8")
                    logger.info(f"[Node: Backend Agent] file  added to the path {str(full_path)}")
                except FileExistsError as e:
                    pass
                state.data["codebase"][file_path] = {
                    "absolute_path": str(full_path),
                    "task_id": task_id
                }
            task["status"] = "FINISHED"
        for t in tasks:
            if t.get("task_id") == task_id:
                t["status"] = "FINISHED"
        return {
            "data": {
                **state.data,
                "tasks": tasks,
                "devops_tasks": devops_tasks,
                "codebase": state.data["codebase"]
            }
        }