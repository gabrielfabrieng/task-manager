"""Celery tasks for the tasks app (async side-effects)."""

from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import TaskShare

logger = logging.getLogger("apps.tasks")


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_share_notification(self, share_id: int) -> None:
    """E-mail the recipient that a task was shared with them.

    Runs off the request thread so sharing responds instantly. Retries on
    transient mail failures.
    """
    try:
        share = TaskShare.objects.select_related("task", "task__owner", "user").get(
            id=share_id
        )
    except TaskShare.DoesNotExist:
        logger.warning("share %s vanished before notification", share_id)
        return

    try:
        send_mail(
            subject=f'"{share.task.title}" was shared with you',
            message=(
                f"{share.task.owner.username} shared the task "
                f'"{share.task.title}" with you ({share.permission} access).'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[share.user.email],
            fail_silently=False,
        )
    except Exception as exc:  # noqa: BLE001 - retry any transient mail error
        raise self.retry(exc=exc)
