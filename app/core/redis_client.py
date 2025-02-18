# import redis.asyncio as redis
# from app.core.config import settings
#
# redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

import redis.asyncio as aioredis
from app.core.config import settings
import os


class RedisConnectionManager:
    # _redis_host = redis_host
    # _redis_port = redis_port
    # _redis_password = redis_password

    # redis_pool = None

    @classmethod
    async def establish_connection(self):
        self.redis_pool = await aioredis.from_url(
            settings.REDIS_URL,
            # password=self._redis_password,
            decode_responses=True,
            max_connections=10
        )

        return True

    @classmethod
    async def get_redis_connection(self):
        if self.redis_pool is None:
            await self.establish_connection()
        return self.redis_pool

    @classmethod
    async def check_redis_connection(self):
        try:
            redis_conn = await self.get_redis_connection()
            # value = await redis_conn.get("kamlesh")
            # value = await redis_conn.hget("Kdata", "kamlesh")
            pong = await redis_conn.ping()
            if pong:
                print("Redis Connection Established")
                return True
        except Exception as e:
            print(f"Redis Connection Check Failed: {e}")
            return False

