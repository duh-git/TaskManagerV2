from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Наполняет базу данных тестовыми пользователями и задачами"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Количество создаваемых задач (по умолчанию 50)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие данные перед созданием",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if clear:
            self.clear_data()

        self.create_users()
        self.create_tasks(count)

        self.stdout.write(self.style.SUCCESS(f"Успешно создано {count} тестовых задач"))

    def clear_data(self):
        Task.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Все данные очищены"))


    def create_users(self):
        users_data = [
            {
                "username": "manager",
                "email": "manager@example.com",
                "password": "manager123",
            },
            {"username": "dev1", "email": "dev1@example.com", "password": "dev1123"},
            {"username": "dev2", "email": "dev2@example.com", "password": "dev2123"},
            {"username": "tester", "email": "tester@example.com", "password": "tester123"},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={"email": user_data["email"], "is_staff": True},
            )
            if created:
                user.set_password(user_data["password"])
                user.save()

        self.stdout.write(self.style.SUCCESS("Созданы тестовые пользователи"))


    def create_tasks(self, count):
        statuses = ["new", "in_progress", "completed", "cancelled"]
        priorities = [1, 2, 3, 4, 5]
        users = list(User.objects.all())

        for i in range(1, count + 1):
            due_date = timezone.now() + timedelta(days=random.randint(-5, 30))
            start_date = timezone.now() + timedelta(days=random.randint(-10, 5))

            task = Task.objects.create(
                title=f"Тестовая задача #{i}",
                description=f"Описание тестовой задачи #{i}. Это автоматически созданная задача для тестирования системы.",
                status=random.choice(statuses),
                priority=random.choice(priorities),
                start_date=start_date if random.choice([True, False]) else None,
                due_date=due_date if random.choice([True, False]) else None,
                assigned_to=(
                    random.choice(users) if random.choice([True, False]) else None
                ),
            )

            if task.status == "completed":
                task.completed_at = timezone.now()
                task.save()

        # Создаем несколько задач с высоким приоритетом
        for i in range(1, 6):
            Task.objects.create(
                title=f"ВАЖНО: Срочная задача #{i}",
                description=f"Это высокоприоритетная задача, требующая немедленного внимания!",
                status=random.choice(["new", "in_progress"]),
                priority=random.choice([4, 5]),
                due_date=timezone.now() + timedelta(days=random.randint(1, 3)),
            )
