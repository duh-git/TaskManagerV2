# tasks/filters.py
import django_filters
from django.db.models import Q
from .models import Task, User
from django.utils import timezone
from datetime import timedelta


class TaskFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    priority = django_filters.NumberFilter(field_name="priority")
    due_date = django_filters.DateFilter(field_name="due_date")
    due_date__gte = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date__lte = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")
    assigned_to = django_filters.ModelChoiceFilter(
        field_name="assigned_to", queryset=User.objects.all(), label="Исполнитель"
    )

    class Meta:
        model = Task
        fields = ["status", "priority", "due_date", "assigned_to"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )

    @property
    def qs(self):
        queryset = super().qs
        if "high_priority" in self.request.GET:
            queryset = queryset.filter(priority__gte=3, status__ne="completed")
        if "due_soon" in self.request.GET:
            soon = timezone.now() + timedelta(days=7)
            queryset = queryset.filter(due_date__gte=timezone.now(), due_date__lte=soon)
        return queryset
