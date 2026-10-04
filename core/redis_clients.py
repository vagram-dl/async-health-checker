import json
import asyncio
import os

USE_MOCK = os.getenv("USE_MOCK_REDIS", "True").lower() == "true"

if USE_MOCK:
    print("ВНИМАНИЕ: Используется MOCK REDIS (локальная разработка)")


    class MockAsyncRedis:
        def __init__(self):
            self._queues = {}
            self._events = {}

        async def lpush(self, key: str, value: str):
            if key not in self._queues:
                self._queues[key] = []
            self._queues[key].insert(0, value)
            print(f"[MOCK REDIS] Успешно добавлено в '{key}'. Элементов: {len(self._queues[key])}")

            if key in self._events:
                self._events[key].set()
            return len(self._queues[key])

        async def rpop(self, key: str):
            if key in self._queues and self._queues[key]:
                value = self._queues[key].pop()
                print(f"[MOCK REDIS] Успешно извлечено из '{key}'. Осталось: {len(self._queues[key])}")
                return value
            return None

        async def brpop(self, key: str, timeout: int = 0):
            if key not in self._queues:
                self._queues[key] = []
            if key not in self._events:
                self._events[key] = asyncio.Event()

            while True:
                if self._queues[key]:
                    value = self._queues[key].pop()
                    print(f"[MOCK REDIS BRPOP] Мгновенно извлечено из '{key}'. Осталось: {len(self._queues[key])}")
                    return (key, value)

                try:
                    await asyncio.wait_for(
                        self._events[key].wait(),
                        timeout=timeout if timeout > 0 else None
                    )
                    self._events[key].clear()
                except asyncio.TimeoutError:
                    print(f"[MOCK REDIS BRPOP] Таймаут {timeout} сек. для очереди '{key}'")
                    return None

        async def ping(self):
            return True


    redis_client = MockAsyncRedis()

else:
    print("Подключение к НАСТОЯЩЕМУ Redis...")
    import redis.asyncio as redis

    REAL_REDIS_URL = os.getenv("REDIS_URL", "redis://72.56.250.97:6379/0")
    redis_client = redis.from_url(REAL_REDIS_URL, decode_responses=True)


async def check_redis_connection():
    try:
        result = await redis_client.ping()
        if result:
            print("Redis подключен и работает успешно!")
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")