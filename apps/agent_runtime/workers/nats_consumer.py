from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
def task_event_handler(payload: dict, metadata: dict):
    logger.info("Received Workflow task event from workflow.event.task.created")
    try:
        if payload["task_id"]:
            agent_execution_loop(payload = payload, metadata = metadata)
        else:
            logger.error("Task_id is not found in the received event ")
    except Exception as e:
        logger.error("")
    pass
