import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from apps.agent_runtime.memory.base import BaseMemoryStore
import redis.asyncio as redis


class RedisShortTermMemoryStore(BaseMemoryStore):
    """
    Manages short-term execution memory (messages, intermediate tool calls,
    observations, decisions) during a single run using Redis.
    """
    def __init__(self, redis_url: str, default_ttl_seconds: int = 86400):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.ttl = default_ttl_seconds

    async def store(self,entity_id: UUID,key: str,value: Any,metadata: Optional[Dict[str, Any]] = None) -> None:
        """Stores short-term transient state or message history."""
        cache_key = f"short_term:{entity_id}:{key}"
        payload = {
            "value": value,
            "metadata": metadata or {}
        }
        await self.redis.set(cache_key, json.dumps(payload), ex=self.ttl)
        logger.debug(f"Stored short-term memory for run/entity {entity_id} under '{key}'")

    async def retrieve(self, entity_id: UUID, key: str) -> Optional[Any]:
        """Retrieves short-term transient state."""
        cache_key = f"short_term:{entity_id}:{key}"
        data = await self.redis.get(cache_key)
        if not data:
            return None
        parsed = json.loads(data)
        return parsed.get("value")

    async def search(self, entity_id: UUID, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Short-term Redis memory typically uses exact key lookups rather than vector search."""
        logger.warning("Search is not natively optimized for Redis short-term key-value stores. Use PostgresVectorMemoryStore for semantic search.")
        return []

    async def delete(self, entity_id: UUID, key: str) -> None:
        """Clears short-term state upon run completion or expiration."""
        cache_key = f"short_term:{entity_id}:{key}"
        await self.redis.delete(cache_key)
        logger.debug(f"Deleted short-term memory '{key}' for entity {entity_id}")