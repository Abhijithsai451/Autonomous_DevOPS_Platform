import platform

from langchain_core.tools import tool
from opentelemetry.sdk.resources import psutil


@tool
def get_system_status()-> dict:
    """
    Returns basic system diagnostic metrics including platform, CPU and memory utilization
    """
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_usage_percent": psutil.cpu_percent(interval= None),
        "memory_usage_percent": psutil.virtual_memory().percent,
        "status": "OPERATIONAL",
    }

DEFAULT_TOOLS = [get_system_status]
TOOLS_BY_NAME = {t.name for t in DEFAULT_TOOLS}

