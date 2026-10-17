from apps.agent_runtime.config.settings import agent_runtime_settings
from apps.agent_runtime.infrastructure.struct_logger import struct_logger as logger
from infrastructure.redis.client import RedisMemoryCache

def redis_connect(url)-> RedisMemoryCache:
    logger.info("connecting to the Redis Client ...")
    try:
        redis_memory = RedisMemoryCache(url)

    except Exception as e:
        raise Exception(f"Could not connect to the Redis server {e}. Check connection url {url} ")

    return redis_memory


agent_redis_client = redis_connect(agent_runtime_settings.REDIS_HOST())
