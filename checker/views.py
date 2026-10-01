import uuid
from turtle import readconfig

from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .serializers import TaskCreateSerializer, CheckResultSerializer
from .models import CheckResult

class CreateTaskView(APIView):
    @extend_schema(request=TaskCreateSerializer, responses={201:dict})
    async def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        urls = serializer.validated_data['urls']

        task_id = uuid.uuid4()

        return Response({
            "task_id":str(task_id),
            "status":"queued",
            "urls_count":len(urls),
            "created_at":timezone.now().isoformat()
        }, status=status.HTTP_201_CREATED)

class GetTaskView(APIView):
    @extend_schema(responses={200: dict})
    async def get(self, request, task_id: uuid.UUID):
        results = CheckResult.objects.filter(task_id=task_id)

        if not results.exists():
            return Response({
                "task_id":str(task_id),
                "status":"processing",
                "total_urls":0,
                "processed_urls":0,
                "results":[]
            })

        return Response({
            "task_id" : str(task_id),
            "status" : "completed",
            "total_urls" : results.count(),
            "processed_urls": results.count(),
            "results":CheckResultSerializer(results, many=True).data
        })
# Create your views here.
