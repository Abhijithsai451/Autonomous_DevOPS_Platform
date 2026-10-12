from apps.tool_gateway.application.mcp_server import mcp
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger

if __name__ == "__main__":
    logger.info("Starting CortexOps Tool Gateway Service...")
    mcp.run(transport="sse")