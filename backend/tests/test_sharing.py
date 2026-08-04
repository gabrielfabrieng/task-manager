"""Task sharing service + async notification."""

from __future__ import annotations

import pytest
from django.core import mail
from django.urls import reverse

from apps.common.exceptions import ConflictError, NotFoundError
from apps.tasks.models import TaskShare
from apps.tasks.services import share_task
from tests.factories import TaskFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_owner_can_share_and_email_sent(auth_client, user, django_capture_on_commit_callbacks):
    task = TaskFactory(owner=user)
    recipient = UserFactory(email="friend@example.com")
    # on_commit callbacks (the Celery enqueue) only run when the tx commits;
    # this fixture executes them so the eager task fires.
    with django_capture_on_commit_callbacks(execute=True):
        resp = auth_client.post(
            reverse("v1:task-share", args=[task.id]),
            {"email": "friend@example.com", "permission": "edit"},
            format="json",
        )
    assert resp.status_code == 201
    assert TaskShare.objects.filter(task=task, user=recipient).exists()
    # Celery runs eagerly in tests -> email lands in the outbox.
    assert len(mail.outbox) == 1
    assert "friend@example.com" in mail.outbox[0].to


def test_share_with_unknown_email_raises():
    task = TaskFactory()
    with pytest.raises(NotFoundError):
        share_task(task=task, recipient_email="ghost@example.com", permission="view")


def test_cannot_share_with_owner():
    task = TaskFactory()
    with pytest.raises(ConflictError):
        share_task(task=task, recipient_email=task.owner.email, permission="view")


def test_duplicate_share_raises():
    task = TaskFactory()
    recipient = UserFactory()
    share_task(task=task, recipient_email=recipient.email, permission="view")
    with pytest.raises(ConflictError):
        share_task(task=task, recipient_email=recipient.email, permission="view")


def test_shared_task_visible_to_recipient(api_client, other_user):
    recipient = UserFactory()
    task = TaskFactory(owner=other_user, title="shared one")
    TaskShare.objects.create(task=task, user=recipient)
    api_client.force_authenticate(user=recipient)
    resp = api_client.get(reverse("v1:task-list"))
    assert [t["title"] for t in resp.data["results"]] == ["shared one"]
