import asyncio
from core.redis_clients import redis_client
from checker.consumer import process_task

async def test_corrupted_data():
    print("=" * 60)
    print("ТЕСТ 1: Проверка устойчивости к битым данным")
    print("=" * 60)

    bad_tasks = [
        ("Тест 1: Невалидный JSON (одинарные кавычки)", "{'task_id':'1', 'urls':[]}"),
        ("Тест 2: Отсутствует ключ task_id", '{"urls": ["https://ya.ru"]}'),
        ("Тест 3: Отсутствует ключ urls", '{"task_id": "test-2"}'),
        ("Тест 4: urls - это не список, а строка", '{"task_id": "test-3", "urls": "not_a_list"}'),
        ("Тест 5: Пустой список urls (валидно, но граничный случай)", '{"task_id": "test-4", "urls": []}'),
    ]
    for desc, bad_data in bad_tasks:
        print(f"\n--- {desc} ---")
        print(f"Данные в очереди: {bad_data}")

        await redis_client.lpush("task_queue", bad_data)

        task_json = await redis_client.rpop("task_queue")
        if task_json:
            await process_task(task_json)
        print("Обработка завершена (воркер не упал!)")

    print("\n" + "=" * 60)
    print("ТЕСТ 1 ПРОЙДЕН УСПЕШНО! Все битые данные обработаны корректно.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_corrupted_data())