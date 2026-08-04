"""
Task domain services — the single home for task business rules.

Views call these; Celery tasks call these; tests call these directly. No HTTP,
no serializer knowledge here.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet

from apps.common.exceptions import ConflictError, NotFoundError

from .models import Task, TaskShare

User = get_user_model()


def tasks_visible_to(user) -> QuerySet[Task]:
    """Tasks a user may see: owned OR shared with them. Basis for queryset scoping."""
    return (
        Task.objects.filter(Q(owner=user) | Q(shares__user=user))
        .distinct()
        .select_related("owner", "category")
    )


def set_status(*, task: Task, done: bool) -> Task:
    """Mark a task done / not-done (requirement f)."""
    task.status = Task.Status.DONE if done else Task.Status.PENDING
    task.save(update_fields=["status", "updated_at"])
    return task


@transaction.atomic
def share_task(*, task: Task, recipient_email: str, permission: str) -> TaskShare:
    """Share ``task`` with the user identified by ``recipient_email``.

    Raises NotFoundError if no such user, ConflictError on self-share/duplicate.
    Sends an async notification e-mail (fire-and-forget) after commit.
    """
    try:
        recipient = User.objects.get(email__iexact=recipient_email)
    except User.DoesNotExist as exc:
        raise NotFoundError("No user with that e-mail.") from exc

    if recipient.id == task.owner_id:
        raise ConflictError("Cannot share a task with its owner.")

    try:
        share = TaskShare.objects.create(task=task, user=recipient, permission=permission)
    except IntegrityError as exc:
        raise ConflictError("Task already shared with this user.") from exc

    # Import here to avoid a circular import at module load.
    from .tasks import send_share_notification

    transaction.on_commit(lambda: send_share_notification.delay(share_id=share.id))
    return share


def unshare_task(*, task: Task, user_id: int) -> None:
    deleted, _ = TaskShare.objects.filter(task=task, user_id=user_id).delete()
    if not deleted:
        raise NotFoundError("Share not found.")
