import json
from typing import List, Dict, Any

code_orch_system_prompt = """You are a Principal Software Engineer specializing in {role}.
Your objective is to implement production-grade, clean, maintainable code based strictly on assigned engineering tasks and specifications.

Standards:
1. Complete, Functional Code: Never emit placeholders, `TODO`, or `...`. Provide complete file implementations.
2. Architecture & Idioms: Adhere to strict typing, standard project design patterns, robust error handling, and clean separation of concerns.
3. Target Files: Map each implementation precisely to the specified file path.

Output Format:
You MUST respond STRICTLY with a valid JSON object matching:
{{
  "artifacts": [
    {{
      "filepath": "path/to/file.py",
      "content": "<Complete source code>",
      "action": "CREATE" | "MODIFY"
    }}
  ],
  "notes": "<Brief implementation notes or dependencies introduced>"
}}
"""


BACKEND_SYSTEM_PROMPT = code_orch_system_prompt.format(role="Backend Systems, APIs, Database Models, and Business Logic")
FRONTEND_SYSTEM_PROMPT = code_orch_system_prompt.format(role="Frontend UI, Component State Management, and Client API Integration")
DEVOPS_SYSTEM_PROMPT = code_orch_system_prompt.format(role="DevOps, Docker, CI/CD, Infrastructure as Code, and Kubernetes Manifests")


def build_specialist_prompt(role_name: str,
                            assigned_tasks: List[Dict[str, Any]],
                            task_spec: Dict[str, Any]) -> str:
    """Builds the input prompt for an individual specialist coding agent."""
    tasks_json = json.dumps(assigned_tasks, indent=2)
    spec_summary = task_spec.get("executive_summary", "")
    constraints = json.dumps(task_spec.get("architectural_constraints", []), indent=2)

    return f"""### ROLE: {role_name}
            
            ### PROJECT SPECIFICATION SUMMARY
            {spec_summary}
            
            ### ARCHITECTURAL CONSTRAINTS
            {constraints}
            
            ### ASSIGNED TASKS TO IMPLEMENT
            \"\"\"json
            {tasks_json}
            \"\"\"
            
            Implement all assigned tasks and return the generated code artifacts according to the required JSON schema.
            """