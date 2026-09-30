import sys
import io
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CodeExecutionInput(BaseModel):
    code: str = Field(
        ...,
        description="The Python code to execute. Standard output will be captured and returned.",
    )

@tool("python_interpreter", args_schema=CodeExecutionInput)
def safe_python_interpreter(code: str) -> str:
    """
    Executes Python code in a restricted scope and captures printed stdout output.
    """
    # Prevent dangerous built-in usage
    restricted_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "sum": sum,
            "max": max,
            "min": min,
            "abs": abs,
        }
    }

    buffer = io.StringIO()
    old_stdout = sys.stdout

    try:
        sys.stdout = buffer
        exec(code, restricted_globals, {})
        output = buffer.getvalue()
        return (
            output.strip()
            if output
            else "Code executed successfully with no output."
        )
    except Exception as exc:
        return f"Execution Error: {type(exc).__name__}: {str(exc)}"
    finally:
        sys.stdout = old_stdout