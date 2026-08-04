"""Query filters for tasks (OWASP-safe: field-scoped, no raw SQL)."""

from __future__ import annotations

import django_filters as filters

from .models import Task


class TaskFilter(filters.FilterSet):
    """Filter tasks by status, category, and due-date window.

    Examples:
      /tasks/?status=done
      /tasks/?category=3
      /tasks/?due_before=2026-01-01T00:00:00Z
    """

    status = filters.ChoiceFilter(choices=Task.Status.choices)
    category = filters.NumberFilter(field_name="category_id")
    due_before = filters.IsoDateTimeFilter(field_name="due_date", lookup_expr="lte")
    due_after = filters.IsoDateTimeFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ["status", "category", "due_before", "due_after"]
