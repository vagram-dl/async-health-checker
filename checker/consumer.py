import json
import asyncio
from core.redis_clients import redis_client

async def process_task(task_json:str):
    try:
        task_data = json.loads(task_json)
        task_id = task_data["task_id"]
        urls = task_data["urls"]

        print(f"Начинаю обработку задачи {task_id}")
        print(f"URL-адресов для проверки: {len(urls)}")

        # results = await check_urls(urls)
        # await save_results(task_id, results)

        print(f"Задача {task_id} успешно обработана!")

    except json.JSONDecodeError:
        print("Ошибка: не удалось распарсить JSON задачи")
    except Exception as e:
        print(f"Ошибка при обработке задачи {e}")

async def run_worker():
    print("Запуск воркера. Ожидание задач в очереди 'task_queue'...")

    while True:
        try:
            task_json = await redis_client.rpop("task_queue")

            if task_json:
                await process_task(task_json)
            else:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Критическая ошибка в цикле воркера: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_worker())
