import json
import uuid
from unittest.mock import patch, AsyncMock
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from checker.models import CheckResult
from checker.producer import send_task_to_redis

class TaskAPITests(APITestCase):
    def test_create_task_success(self):
        url = reverse('create_task')
        data = {
            "urls": [
                "https://ya.ru",
                "https://google.com"
            ]
        }

        with patch('checker.views.send_task_to_redis', new_callable=AsyncMock) as mock_redis:
            response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['status'], 'queued')
        self.assertEqual(response.data['urls_count'], 2)

        mock_redis.assert_called_once()

    def test_create_task_invalid_urls(self):
        url = reverse('create_task')
        data = {
            "urls" : [
                "not-a-valid-url",
                "https://google.com"
            ]
        }

        response = self.client.post(url,data,format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('urls', response.data)

    def test_create_task_empty_urls(self):
        url = reverse('create_task')
        data = {
            "urls": []
        }

        response = self.client.post(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_get_task_results_processing(self):
        task_id = uuid.uuid4()
        url = f'/api/v1/task/{task_id}'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'processing')
        self.assertEqual(response.data['total_urls'], 0)
        self.assertEqual(response.data['processed_urls'], 0)
        self.assertEqual(response.data['results'], [])

    def test_get_task_results_completed(self):
        task_id = uuid.uuid4()

        CheckResult.objects.create(
            task_id=task_id,
            url="https://ya.ru",
            status_code=200,
            response_time=150.5,
            is_available=True,
            error_message=None
        )
        CheckResult.objects.create(
            task_id=task_id,
            url="https://google.com",
            status_code=200,
            response_time=212.7,
            is_available=True,
            error_message=None
        )

        url = f'/api/v1/task/{task_id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['total_urls'], 2)
        self.assertEqual(response.data['processed_urls'], 2)
        self.assertEqual(len(response.data['results']), 2)

        first_result = response.data['results'][0]
        self.assertIn('url', first_result)
        self.assertIn('status_code', first_result)
        self.assertIn('response_time', first_result)
        self.assertIn('is_available', first_result)
        self.assertIn('checked_at', first_result)


class ProducerTests(TestCase):

    def test_send_task_to_redis(self):
        task_id = str(uuid.uuid4())
        urls = ["https://ya.ru", "https://google.com"]

        with patch('checker.producer.redis_client') as mock_redis:
            mock_redis.lpush = AsyncMock()

            import asyncio
            asyncio.run(send_task_to_redis(task_id, urls))

            mock_redis.lpush.assert_called_once()

            call_args = mock_redis.lpush.call_args
            queue_name = call_args[0][0]
            task_json = call_args[0][1]

            self.assertEqual(queue_name, 'task_queue')

            task_data = json.loads(task_json)
            self.assertEqual(task_data['task_id'], task_id)
            self.assertEqual(task_data['urls'], urls)

# Create your tests here.
