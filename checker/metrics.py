from prometheus_client import Counter,Gauge

tasks_processed_total = Counter(
    'tasks_processed_total',
    'Total number of processed tasks'
)

urls_checked_total = Counter(
    'urls_checked_total',
    'Total number of checked URLs',
    ['status']
)

active_workers = Gauge(
    'active_workers',
    'Current number of active workers'
)