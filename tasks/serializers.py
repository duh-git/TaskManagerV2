# tasks/serializers.py
from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",
        write_only=True,
        required=False,
        allow_null=True,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "completed_at"]

    def validate_priority(self, value):
        if value not in dict(Task.PRIORITY_CHOICES).keys():
            raise serializers.ValidationError("Priority must be between 1 and 5")
        return value

    def validate(self, data):
        if data.get("start_date") and data.get("due_date"):
            if data["start_date"] > data["due_date"]:
                raise serializers.ValidationError(
                    "Start date cannot be later than due date"
                )
        return data


class TaskHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField()

    class Meta:
        model = Task.history.model  # Используем модель истории из simple-history
        fields = [
            "history_date",
            "history_user",
            "history_change_reason",
            "status",
            "priority",
            "due_date",
        ]
        read_only_fields = fields
