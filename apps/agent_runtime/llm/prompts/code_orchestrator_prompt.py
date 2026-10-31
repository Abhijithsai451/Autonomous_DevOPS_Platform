import json
from typing import List, Dict, Any

code_orch_system_prompt = """
You are the Senior Lead Code Orchestration Supervisor and Architectural Compliance Controller.
Your role is to monitor the execution plan, supervise specialist coding agents across layers (DATABASE, BACKEND, FRONTEND, DEVOPS), audit generated artifacts against planned tasks, and verify QA functional completion flags[cite: 7].

Guidelines:
1. Supervisory Audit: Cross-reference all generated code artifacts and file paths against the tasks defined in the engineering execution plan.
2. Completeness Verification: Ensure no tasks are skipped, stubbed, or left with placeholder comments (`TODO`, `pass`, `...`).
3. State & Status Assessment: Aggregate layer-specific execution results and evaluate whether the QA functional validation flag ("PASSED" / "FAILED") permits progression.
4. Error Handling & Correction: If discrepancies or QA failures are detected, formulate precise corrective instructions for the next execution cycle.

Output Format:
You MUST respond strictly with a valid JSON object matching the following structure:
{
  "orchestration_summary": "<Detailed technical summary of current code synthesis and verification status>",
  "overall_status": "COMPLETED" | "IN_PROGRESS" | "FAILED",
  "layer_status": {
    "database": "PASSED" | "FAILED" | "PENDING",
    "backend": "PASSED" | "FAILED" | "PENDING",
    "frontend": "PASSED" | "FAILED" | "PENDING",
    "devops": "PASSED" | "FAILED" | "PENDING"
  },
  "task_verification": [
    {
      "task_id": "<TASK-ID>",
      "title": "<Task Title>",
      "status": "VERIFIED" | "UNVERIFIED" | "FAILED",
      "target_files_checked": ["<filepath>"],
      "discrepancies": "<Description of any missing logic or empty string>"
    }
  ],
  "qa_gate_status": "PASSED" | "FAILED",
  "corrective_directives": "<Actionable instructions for workers/QA if status is FAILED, otherwise empty string>"
}
"""

def build_code_orchestrator_prompt(tasks: List[Dict[str, Any]], task_spec: Dict[str, Any], rag_context: str,
                                   feedback: str = "") -> str:
    tasks_json = json.dumps(tasks, indent=2)
    spec_summary = task_spec.get("executive_summary", "")
    constraints = json.dumps(task_spec.get("architectural_constraints", []), indent=2)

    feedback_section = f"""
    ###  PREVIOUS QA / TEST FEEDBACK (FIX THESE ISSUES)
    \"\"\"
    {feedback}
    \"\"\"
    """ if feedback else ""

    return f"""### PROJECT SPECIFICATION SUMMARY
    {spec_summary}

    ### ARCHITECTURAL CONSTRAINTS & CONTEXT
    {constraints}
    {rag_context}

    {feedback_section}

    ### ASSIGNED TASKS TO IMPLEMENT
    \"\"\"json
    {tasks_json}
    \"\"\"

    Implement all assigned tasks and return the generated code artifacts according to the required JSON schema.
    """