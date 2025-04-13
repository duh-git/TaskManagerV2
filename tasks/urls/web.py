from django.urls import path
from ..views.web import *

urlpatterns = [
    path("", TaskListView.as_view(), name="task_list"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("<int:pk>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("<int:pk>/assign/", task_assign, name="task_assign"),
    path(
        "<int:pk>/change-status/", change_status, name="task_change_status"
    ),  # Добавляем новый путь
]
