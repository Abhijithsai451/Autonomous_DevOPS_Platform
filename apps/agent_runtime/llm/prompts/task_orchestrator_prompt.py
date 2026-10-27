def build_prompt(query: str, rag_context: str)-> str:
    task_orchestrator_prompt = f"""
                                You are a task orchestrator Agent. Your responsible to understand the task and 
                                divide the task into small steps. 
                                {query} + {rag_context}
                                """

    return task_orchestrator_prompt