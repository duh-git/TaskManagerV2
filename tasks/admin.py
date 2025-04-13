from django.contrib import admin
from django.http import HttpResponse
from import_export import resources, fields
from import_export.admin import ExportActionModelAdmin
from import_export.formats.base_formats import XLSX, CSV, JSON
from django.contrib import messages
from django.utils import timezone
from simple_history.admin import SimpleHistoryAdmin  # Добавлено
from .models import Task


class TaskResource(resources.ModelResource):
    status_display = fields.Field(attribute="status", column_name="Status")
    priority_display = fields.Field(attribute="priority", column_name="Priority")
    assigned_to_username = fields.Field(column_name="Assigned To")
    history_user = fields.Field(column_name="Last Edited By")  # Добавлено

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "status_display",
            "priority_display",
            "created_at",
            "due_date",
            "assigned_to_username",
            "history_user",  # Добавлено
        )
        export_order = fields
        formats = (XLSX, CSV, JSON)

    def dehydrate_status_display(self, task):
        return task.get_status_display()

    def dehydrate_priority_display(self, task):
        return task.get_priority_display()

    def dehydrate_assigned_to_username(self, task):
        return task.assigned_to.username if task.assigned_to else "Not assigned"

    def dehydrate_history_user(self, task):  # Добавлено
        last_change = task.history.first()
        return (
            last_change.history_user.username
            if last_change and last_change.history_user
            else "System"
        )

    def dehydrate_due_date(self, task):
        return task.due_date.strftime("%d-%m-%Y %H:%M") if task.due_date else ""

    def get_export_queryset(self, request):
        queryset = super().get_export_queryset(request)
        if request.GET.get("high_priority_only"):
            return queryset.filter(priority__gte=3)
        return queryset


def export_selected_tasks(modeladmin, request, queryset):
    if not queryset.exists():
        modeladmin.message_user(request, "Нет задач для экспорта", messages.WARNING)
        return

    format = request.POST.get("format", "xlsx")
    resource = TaskResource()
    dataset = resource.export(queryset)

    if format == "xlsx":
        response = HttpResponse(dataset.xlsx, content_type=XLSX.CONTENT_TYPE)
        ext = "xlsx"
    elif format == "csv":
        response = HttpResponse(dataset.csv, content_type=CSV.CONTENT_TYPE)
        ext = "csv"
    else:
        response = HttpResponse(dataset.json, content_type=JSON.CONTENT_TYPE)
        ext = "json"

    response["Content-Disposition"] = (
        f"attachment; filename=tasks_{timezone.now().date()}.{ext}"
    )
    return response


export_selected_tasks.short_description = "Экспорт выбранных задач"


class HighPriorityFilter(admin.SimpleListFilter):
    title = "Приоритет"
    parameter_name = "priority"

    def lookups(self, request, model_admin):
        return (
            ("high", "Высокий приоритет (3+)"),
            ("critical", "Критический (4-5)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "high":
            return queryset.filter(priority__gte=3)
        if self.value() == "critical":
            return queryset.filter(priority__gte=4)
        return queryset


@admin.register(Task)
class TaskAdmin(
    SimpleHistoryAdmin, ExportActionModelAdmin
):  # Изменено: добавлен SimpleHistoryAdmin
    resource_class = TaskResource
    list_display = (
        "title",
        "status",
        "priority",
        "due_date",
        "assigned_to",
        "is_overdue",
        "last_history_date",  # Добавлено
    )
    list_filter = (
        HighPriorityFilter,
        "status",
        ("due_date", admin.DateFieldListFilter),
    )
    search_fields = ("title", "description")
    readonly_fields = (
        "created_at",
        "updated_at",
        "completed_at",
        "last_history_date",
    )  # Добавлено
    date_hierarchy = "due_date"
    actions = [export_selected_tasks, "mark_as_completed"]
    history_list_display = [
        "status",
        "priority",
        "due_date",
    ]  # Какие поля показывать в истории

    fieldsets = (
        (None, {"fields": ("title", "description", "status", "priority")}),
        ("Даты", {"fields": (("start_date", "due_date"), "completed_at")}),
        (
            "Дополнительно",
            {
                "fields": (
                    "assigned_to",
                    ("created_at", "updated_at"),
                    "last_history_date",  # Добавлено
                )
            },
        ),
    )

    def get_export_formats(self):
        return [XLSX, CSV, JSON]

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed", completed_at=timezone.now())
        self.message_user(
            request, f"{updated} задач помечено как выполненные", messages.SUCCESS
        )

    mark_as_completed.short_description = "Пометить как выполненные"

    def is_overdue(self, obj):
        return obj.is_overdue()

    is_overdue.boolean = True
    is_overdue.short_description = "Просрочена"

    # Добавленные методы для истории
    def last_history_date(self, obj):
        last_change = obj.history.first()
        return last_change.history_date if last_change else "Нет изменений"

    last_history_date.short_description = "Последнее изменение"
