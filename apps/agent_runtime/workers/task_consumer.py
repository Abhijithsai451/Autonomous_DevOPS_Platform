from apps.agent_runtime.infrastructure.struct_logger import struct_logger


class InvalidTaskEvent(ValueError):
    """Incoming Task does not match the expected contract"""


def task_event_handler(payload: dict, metadata: dict):
    dept_id = payload.get("id")
    description = payload.get("description")

    struct_logger.info(f"  Workflow Service received DepartmentCreated: Dept ID={dept_id}, Description='{description}'")

