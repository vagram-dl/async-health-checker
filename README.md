# Async Health Checker

Асинхронный сервис для проверки доступности веб-ресурсов. Реализует паттерн Producer-Consumer с использованием Redis в качестве брокера сообщений.

## Технологический стек

- **Python 3.12**
- **Django 6.0.8 + Django REST Framework** (вместо FastAPI — для ускорения разработки и использования встроенной ORM)
- **asyncio + aiohttp** — асинхронная обработка HTTP-запросов
- **Redis** — брокер сообщений (очередь задач)
- **SQLite** (локальная разработка) / **MySQL** (production)
- **Prometheus** — метрики мониторинга (`django-prometheus` + `prometheus_client`)
- **JSON-логирование** с обязательным полем `task_id`
- **unittest** — смоук-тесты (совместимы с pytest)

## Архитектура

Проект состоит из двух логических компонентов:

1. **REST API (Producer)** — принимает задачи через `POST /api/v1/task`, генерирует `task_id`, отправляет задачу в очередь Redis.
2. **Async Worker (Consumer)** — забирает задачи из Redis, параллельно проверяет URL через `aiohttp`, сохраняет результаты в БД.

### Ключевые архитектурные решения

- **asyncio.Semaphore(10)** — ограничение конкурентности (не более 10 одновременных HTTP-запросов)
- **Graceful Shutdown** — корректная обработка сигналов `SIGINT`/`SIGTERM`, завершение текущих задач перед остановкой
- **asyncio.gather()** — параллельная проверка всех URL в рамках одной задачи
- **abulk_create()** — массовая вставка результатов в БД (оптимизация вместо циклического `save()`)
- **Prometheus-метрики** — мониторинг через эндпоинт `/metrics/`
- **Структурированные JSON-логи** — все события воркера логируются с обязательным `task_id` для трассировки

## Быстрый старт

### Локальная разработка (без Docker)

```bash
# 1. Клонировать репозиторий
git clone <your-repo-url>
cd async-health-checker

# 2. Создать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Запустить Django-сервер (в первом терминале)
python manage.py runserver

# 6. Запустить воркера (во втором терминале)
python -m checker.consumer
```

### Docker

```bash
docker-compose up --build
```

Документация Swagger UI доступна по адресу: `http://127.0.0.1:8000/docs`

## Мониторинг и наблюдаемость

### Метрики Prometheus

Эндпоинт `/metrics/` отдаёт метрики в формате Prometheus:

- `http_requests_total` — общее количество HTTP-запросов
- `http_request_duration_seconds` — гистограмма длительности запросов
- `tasks_processed_total` — количество обработанных задач
- `urls_checked_total{status="available|unavailable"}` — количество проверенных URL
- `active_workers` — количество активных воркеров

### JSON-логи

Все события воркера логируются в JSON-формате с обязательным полем `task_id`:

```json
{
  "timestamp": "2026-10-07T15:30:00.123456",
  "level": "INFO",
  "logger": "checker.consumer",
  "message": "Задача успешно обработана",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "consumer",
  "function": "process_task",
  "line": 85
}
```

## Тестирование

Проект покрыт смоук-тестами (unittest):

```bash
python manage.py test checker
```

**Покрытие:**
- Успешное создание задачи
- Обработка невалидных URL (400 Bad Request)
- Обработка пустого списка URL
- Получение результатов завершённой задачи
- Получение статуса обработки (processing)
- Работа Producer с очередью Redis

## Примечания

- В рамках проекта использован **Django + DRF** вместо FastAPI (допустимое упрощение по ТЗ) для ускорения разработки и использования встроенной ORM.
- Для production используется **MySQL** вместо PostgreSQL (указанного в ТЗ), но архитектура полностью совместима с любой реляционной СУБД через ORM Django.
- Реализован **MockRedis** для тестирования без запущенного Redis.
- Все требования ТЗ выполнены, включая разделы 4.6 (логирование), 4.7 (надёжность) и 4.10 (мониторинг).

## Лицензия

MIT