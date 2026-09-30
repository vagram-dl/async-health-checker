from django.db import models
import uuid

class CheckResult(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    url = models.CharField(max_length=2048)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Время ответа в миллисекундах")
    is_available = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'check_results'
        indexes = [
            models.Index(fields=['task_id']),
        ]
        verbose_name = 'Результат проверки'
        verbose_name_plural = 'Результаты проверок'

    def __str__(self):
        status = 'ОК' if self.is_available else 'FAIL'
        return f"Task {self.task_id} - {self.url} ({status})"

# Create your models here.
