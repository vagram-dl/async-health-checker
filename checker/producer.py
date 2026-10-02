import json
from core.redis_clients import redis_client

async def send_task_to_redis(task_id: str, urls:list):
    task_data = {
        "task_id":task_id,
        "urls":urls
    }

    task_json = json.dumps(task_data)
    await redis_client.lpush("task_queue",task_json)
    print(f"Задача {task_id} отправлена в Redis")