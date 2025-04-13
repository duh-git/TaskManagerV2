from django import template
from django.db import models

register = template.Library()


@register.filter
def get_changes(record, prev_record):
    """Возвращает список измененных полей между двумя записями"""
    changes = []
    if not prev_record:
        return changes

    fields_to_check = [
        "status",
        "priority",
        "due_date",
        "assigned_to",
        "title",
        "description",
    ]

    for field in fields_to_check:
        old_value = getattr(prev_record, field, None)
        new_value = getattr(record, field, None)

        if old_value != new_value:
            changes.append({"field": field, "old": old_value, "new": new_value})

    return changes


@register.filter
def display_value(value, field_name=None):
    """Форматирует значение для отображения"""
    if value is None:
        return "пусто"

    # Для полей choices
    if field_name and hasattr(value, f"get_{field_name}_display"):
        return getattr(value, f"get_{field_name}_display")()

    # Для ForeignKey
    if isinstance(value, models.Model):
        return str(value)

    # Для дат
    if hasattr(value, "strftime"):
        return value.strftime("%d.%m.%Y %H:%M")

    return str(value)
