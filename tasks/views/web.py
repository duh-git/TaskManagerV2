from django.views.generic import *
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from ..models import Task
from ..forms import TaskForm
from datetime import timedelta
from django.contrib.auth import get_user_model


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Базовые фильтры
        if status := self.request.GET.get("status"):
            queryset = queryset.filter(status=status)
        if priority := self.request.GET.get("priority"):
            queryset = queryset.filter(priority=priority)
        if assigned_to := self.request.GET.get("assigned_to"):
            queryset = queryset.filter(assigned_to__id=assigned_to)

        # Новые фильтры
        if "next_7_days" in self.request.GET:
            soon = timezone.now() + timedelta(days=7)
            queryset = queryset.filter(due_date__gte=timezone.now(), due_date__lte=soon)

        if "high_priority" in self.request.GET:
            queryset = queryset.filter(priority__gte=3)

        if "overdue" in self.request.GET:
            queryset = queryset.filter(
                due_date__lt=timezone.now(), status__in=["new", "in_progress"]
            )

        # Поиск по названию и описанию
        if search := self.request.GET.get("search"):
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # Сортировка
        sort = self.request.GET.get("sort")
        order = self.request.GET.get("order", "asc")

        if sort in ["status", "priority", "due_date"]:
            if order == "desc":
                sort = f"-{sort}"
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by("-priority", "due_date")

        return queryset

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Task.STATUS_CHOICES
        context["priority_choices"] = Task.PRIORITY_CHOICES
        context["current_sort"] = self.request.GET.get("sort")
        context["current_order"] = self.request.GET.get("order", "asc")
        context["assignees"] = User.objects.filter(tasks__isnull=False).distinct()
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history"] = self.object.history.all().order_by("-history_date")
        context["assignable_users"] = (
            get_user_model().objects.filter(is_active=True).order_by("username")
        )
        context["status_choices"] = Task.STATUS_CHOICES
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Задача успешно создана!")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    context_object_name = "task"

    def get_success_url(self):
        messages.success(self.request, "Задача успешно обновлена!")
        return reverse_lazy("task_detail", kwargs={"pk": self.object.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")
    context_object_name = "task"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Задача успешно удалена!")
        return super().delete(request, *args, **kwargs)


def change_status(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get("status")

        if new_status in dict(Task.STATUS_CHOICES).keys():
            task.status = new_status
            if new_status == "completed":
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, "Статус задачи обновлен!")
        else:
            messages.error(request, "Неверный статус!")

    return redirect("task_detail", pk=pk)


def overdue_tasks(request):
    overdue = Task.objects.filter(
        due_date__lt=timezone.now(), status__in=["new", "in_progress"]
    ).order_by("-priority", "due_date")

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": overdue,
            "title": "Просроченные задачи",
            "status_choices": Task.STATUS_CHOICES,
            "priority_choices": Task.PRIORITY_CHOICES,
        },
    )


def change_status(request, pk):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get("status")

        if new_status in dict(Task.STATUS_CHOICES).keys():
            task.status = new_status
            if new_status == "completed":
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, "Статус задачи обновлен!")
        else:
            messages.error(request, "Неверный статус!")

    return redirect("task_detail", pk=pk)


@login_required
def task_assign(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        user_id = request.POST.get("assigned_to")

        if user_id:
            user = get_user_model().objects.get(id=user_id)
            task.assigned_to = user
            message = f"Исполнитель изменен на {user.username}"
        else:
            task.assigned_to = None
            message = "Исполнитель удален"

        task.save()
        messages.success(request, message)

    return redirect("task_detail", pk=pk)
