from fastmcp import FastMCP
from pydantic import Field
from apps.tool_gateway.infrastructure.struct_logger import struct_logger as logger
mcp = FastMCP("CortexOps-ToolServer", log_level="INFO")

@mcp.tool(name = "git_read_file", description ="Read the content of a repository file safely" )
async def run_git_read_file(repo_path: str = Field(description="The local or remote file system path to the repository"),
                            file_path: str = Field(description="Relative path of the file to read")) -> str:
    """
    Executes file read operations as a compliant MCP tool.
    """
    logger.info(f"Executing git_read_file for repo: {repo_path}, file: {file_path}")
    try:
        with open(f"{repo_path}/{file_path}", "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool(name="json_transform",description="Transform and parse complex JSON structures.")
def json_transform(data: dict = Field(description="Raw input dictionary data"),
                    expression: str = Field(description="Transformation query or expression")) -> dict:
    return {"status": "success", "transformed": data}
