import json
import asyncio


class MockAsyncRedis:
    def __init__(self):
        self._queues = {}
        self._events = {}

    async def lpush(self, key: str, value: str):
        if key not in self._queues:
            self._queues[key] = []
        self._queues[key].insert(0, value)
        print(f"[MOCK REDIS] Успешно добавлено в '{key}'. Элементов в очереди: {len(self._queues[key])}")

        if key in self._events:
            self._events[key].set()
        return len(self._queues[key])

    async def rpop(self, key: str):
        if key in self._queues and self._queues[key]:
            value = self._queues[key].pop()
            print(f"[MOCK REDIS] Успешно извлечено из '{key}'. Осталось элементов: {len(self._queues[key])}")
            return value
        return None

    async def brpop(self,key: str, timeout: int = 0):
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
                    timeout = timeout if timeout > 0 else None
                )
                self._events[key].clear()
            except asyncio.TimeoutError:
                print(f"[MOCK REDIS BRPOP] Таймаут {timeout} сек. для очереди '{key}'")

    async def ping(self):
        return True

redis_client = MockAsyncRedis()

async def check_redis_connection():
    try:
        result = await redis_client.ping()
        if result:
            print("Mock Redis подключен и работает успешно!")
    except Exception as e:
        print(f"Ошибка подключения к Mock Redis: {e}")