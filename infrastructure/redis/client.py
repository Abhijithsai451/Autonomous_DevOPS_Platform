import json
from typing import Any, Optional
from uuid import UUID

import redis


class RedisMemoryCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses = True)

    async def set_transient_state(self, run_id: UUID, key: str, value: Any, expire_seconds: int= 3600)-> None:
        cache_key = f"run: {run_id}:{key}"
        await self.redis.set(cache_key, json.dumps(value), ex = expire_seconds)

    async def get_transient_state(self, run_id: UUID, key: str)-> Optional[Any]:
        cache_key = f"run: {run_id}:{key}"
        data = await self.redis.get(cache_key)
        return json.loads(data) if data else None

    async def close(self):
        await self.redis.close()