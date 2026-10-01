from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/task', views.CreateTaskView.as_view(),name = 'create_task'),
    path('api/v1/task/<uuid:task_id>', views.GetTaskView.as_view(), name='get-task'),
]