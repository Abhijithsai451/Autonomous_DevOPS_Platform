from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.stores import InMemoryStore

memory_store = InMemoryStore()

def load_agent_memory(messages: list[BaseMessage], tenant_id: str, agent_id: str) -> list[BaseMessage]:
    """
    Retrieves stored semantic context/user preferences for this agent and prepends it to state messages.
    """
    namespace = (tenant_id, agent_id, "memories")
    memories = memory_store.search(namespace, query="user_preferences")

    if memories:
        memory_text = "\n".join([m.value.get("content", "") for m in memories])
        sys_msg = SystemMessage(content=f"Context from past executions:\n{memory_text}")
        return [sys_msg] + messages

    return messages