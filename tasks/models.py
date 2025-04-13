from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from simple_history.models import HistoricalRecords  # Импорт из simple-history

User = get_user_model()


class Task(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("archived", "Archived"),
    ]

    PRIORITY_CHOICES = [
        (1, "Low"),
        (2, "Medium"),
        (3, "High"),
        (4, "Urgent"),
        (5, "Critical"),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )

    # Добавляем историю
    history = HistoricalRecords(
        excluded_fields=["created_at", "updated_at"],  # Исключаем авто-поля
        history_change_reason_field=models.TextField(null=True),
    )

    class Meta:
        ordering = ["-priority", "due_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["due_date"]),
        ]

    def clean(self):
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError("Start date cannot be later than due date")

        if self.priority not in dict(self.PRIORITY_CHOICES).keys():
            raise ValidationError("Priority must be between 1 and 5")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def is_overdue(self):
        return self.due_date and timezone.now() > self.due_date


