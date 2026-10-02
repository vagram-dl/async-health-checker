import redis.asyncio as redis
from django.conf import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses = True,
    encoding = "utf-8",
    protocol = 2,
    socket_timeout=10,
    socket_connect_timeout=10
)

async def check_redis_connection():
    try:
        await redis_client.ping()
        print("Redis подключен успешно!")
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")