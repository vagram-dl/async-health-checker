from rest_framework import serializers
from .models import CheckResult

class TaskCreateSerializer(serializers.Serializer):
    urls = serializers.ListField(
        child = serializers.URLField(max_length=2048),
        min_length=1,
        help_text="Список URL для проверки"
    )

class CheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckResult
        fields = ['url', 'status_code','response_time','is_available', 'error_message', 'checked_at']