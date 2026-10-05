import json
import asyncio
import time
import aiohttp
from core.redis_clients import redis_client
from checker.models import CheckResult

async def check_single_url(session: aiohttp.ClientSession, url: str)->dict:
    try:
        start_time  = time.time()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total = 10)) as response:
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "url":url,
                "status_code":response.status,
                "response_time_ms": response_time_ms,
                "is_available": response.status < 400,
                "error_message": None
            }
    except asyncio.TimeoutError:
        return {
            "url":url,
            "status_code":None,
            "response_time_ms":None,
            "is_available":False,
            "error_message":"Timeout (10s)"
        }
    except Exception as e:
        return {
            "url":url,
            "status_code":None,
            "response_time_ms":None,
            "is_available":False,
            "error_message":str(e)
        }

async def check_urls(urls: list)->list:
    async with aiohttp.ClientSession() as session:
        tasks = [check_single_url(session,url) for url in urls]
        results = await asyncio.gather(*tasks)
        return list(results)


async def save_results(task_id:str, results:list):
    results_to_create = []

    for res in results:
        results_to_create.append(CheckResult(
            task_id = task_id,
            url = res["url"],
            status_code = res["status_code"],
            response_time = res["response_time_ms"],
            is_available = res["is_available"],
            error_message = res["error_message"]
        ))

    if results_to_create:
        await CheckResult.objects.abulk_create(results_to_create)
        print(f"Успешно сохранено {len(results_to_create)} результатов в БД для задачи {task_id}")
    else:
        print("Нет результатов для сохранения в БД")

async def process_task(task_json:str):
    try:
        task_data = json.loads(task_json)
        task_id = task_data["task_id"]
        urls = task_data["urls"]

        print(f"Начинаю обработку задачи {task_id}")
        print(f"URL-адресов для проверки: {len(urls)}")

        results = await check_urls(urls)
        await save_results(task_id, results)

        print(f"Задача {task_id} успешно обработана!")

    except json.JSONDecodeError:
        print("Ошибка: не удалось распарсить JSON задачи")
    except Exception as e:
        print(f"Ошибка при обработке задачи {e}")

async def run_worker():
    print("Запуск воркера. Ожидание задач в очереди 'task_queue'...")

    while True:
        try:
           result = await redis_client.brpop("task_queue", timeout=10)

           if result:
               queue_name, task_json = result
               print(f"Воркер получил задачу из очереди '{queue_name}'")
               await process_task(task_json)
           else:
               print("Таймаут brpop: задач нет, продолжаем ожидание...")

        except Exception as e:
            print(f"Критическая ошибка в цикле воркера: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_worker())
