"""Domain models: Category, Task and the TaskShare join.

Ownership is explicit on every row (``owner`` FK) so authorization can be
enforced at the object level (OWASP API1 — Broken Object Level Authorization).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

if TYPE_CHECKING:
    from apps.accounts.models import User


class TimeStampedModel(models.Model):
    """Reusable created/updated timestamps (DRY)."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="categories", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=80)
    color = models.CharField(max_length=7, default="#6366f1")  # hex, UI hint

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="uniq_category_name_per_owner")
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DONE = "done", "Done"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="tasks", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category,
        related_name="tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateTimeField(null=True, blank=True)

    shared_with: models.ManyToManyField[User, TaskShare] = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="TaskShare",
        related_name="shared_tasks",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_done(self) -> bool:
        return self.status == self.Status.DONE


class TaskShare(TimeStampedModel):
    """Grants another user access to a task, with a permission level."""

    class Permission(models.TextChoices):
        VIEW = "view", "View"
        EDIT = "edit", "Edit"

    task = models.ForeignKey(Task, related_name="shares", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="task_shares", on_delete=models.CASCADE
    )
    permission = models.CharField(max_length=4, choices=Permission.choices, default=Permission.VIEW)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["task", "user"], name="uniq_share_per_user")]

    def __str__(self) -> str:
        return f"{self.task} -> {self.user} ({self.permission})"
