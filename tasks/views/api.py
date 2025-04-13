from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from ..models import Task
from ..serializers import TaskSerializer, TaskHistorySerializer
from ..filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        # Сложные запросы
        if self.action == "list":
            if "word" in self.request.GET:
                queryset = queryset.filter(
                    description__icontains=self.request.GET["word"]
                )

            if "not_my_tasks" in self.request.GET:
                queryset = queryset.exclude(assigned_to=self.request.user).filter(
                    status__in=["in_progress", "cancelled"]
                )

            if "high_priority_or_tomorrow" in self.request.GET:
                tomorrow = timezone.now() + timedelta(days=1)
                queryset = queryset.filter(
                    Q(priority__gte=3, status__ne="completed")
                    | Q(due_date__date=tomorrow.date())
                )

        return queryset

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get("status")

        if new_status not in dict(Task.STATUS_CHOICES).keys():
            return Response(
                {"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        if new_status == "completed":
            task.completed_at = timezone.now()
        task.save()

        return Response({"status": "changed"})

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        task = self.get_object()
        history = task.history.all()  # Используем simple-history
        serializer = TaskHistorySerializer(history, many=True)
        return Response(serializer.data)


class TaskHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.history.model.objects.all()  # Используем модель истории
    serializer_class = TaskHistorySerializer

    def get_queryset(self):
        task_id = self.request.query_params.get("task_id")
        if task_id:
            return self.queryset.filter(id=task_id)
        return self.queryset.none()
