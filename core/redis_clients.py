import json


class MockAsyncRedis:
    def __init__(self):
        self._queues = {}

    async def lpush(self, key: str, value: str):
        if key not in self._queues:
            self._queues[key] = []
        self._queues[key].insert(0, value)
        print(f"[MOCK REDIS] Успешно добавлено в '{key}'. Элементов в очереди: {len(self._queues[key])}")
        return len(self._queues[key])

    async def rpop(self, key: str):
        if key in self._queues and self._queues[key]:
            value = self._queues[key].pop()
            print(f"[MOCK REDIS] Успешно извлечено из '{key}'. Осталось элементов: {len(self._queues[key])}")
            return value
        return None

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