import redis.asyncio as aioredis
from config import settings

# 全局异步 Redis 实例
redis_client = aioredis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)

async def get_redis():
    return redis_client