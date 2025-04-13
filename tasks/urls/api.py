from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.api import TaskViewSet, TaskHistoryViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
# router.register(
#     r"task-history", TaskHistoryViewSet, basename="task-history"
# )

urlpatterns = [
    path("", include(router.urls)),
]
