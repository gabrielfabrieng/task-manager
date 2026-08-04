"""
Object-level authorization tests (OWASP API1 — BOLA).

These are the most security-relevant tests: they prove a user cannot reach
another user's task by guessing its ID, and that share permission levels are
enforced.
"""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.tasks.models import TaskShare
from tests.factories import TaskFactory

pytestmark = pytest.mark.django_db


def test_cannot_retrieve_foreign_task(auth_client, other_user):
    """Guessing another user's task ID returns 404, never their data."""
    foreign = TaskFactory(owner=other_user)
    resp = auth_client.get(reverse("v1:task-detail", args=[foreign.id]))
    assert resp.status_code == 404


def test_cannot_update_foreign_task(auth_client, other_user):
    foreign = TaskFactory(owner=other_user)
    resp = auth_client.patch(
        reverse("v1:task-detail", args=[foreign.id]),
        {"title": "hijacked"},
        format="json",
    )
    assert resp.status_code == 404


def test_view_share_is_read_only(api_client, user, other_user):
    """A VIEW sharee can read but not modify the task."""
    task = TaskFactory(owner=other_user)
    TaskShare.objects.create(task=task, user=user, permission=TaskShare.Permission.VIEW)
    api_client.force_authenticate(user=user)

    assert api_client.get(reverse("v1:task-detail", args=[task.id])).status_code == 200
    resp = api_client.patch(
        reverse("v1:task-detail", args=[task.id]), {"title": "no"}, format="json"
    )
    assert resp.status_code == 403


def test_edit_share_can_update_but_not_delete(api_client, user, other_user):
    task = TaskFactory(owner=other_user)
    TaskShare.objects.create(task=task, user=user, permission=TaskShare.Permission.EDIT)
    api_client.force_authenticate(user=user)

    upd = api_client.patch(
        reverse("v1:task-detail", args=[task.id]), {"title": "ok"}, format="json"
    )
    assert upd.status_code == 200

    # Delete stays owner-only even for EDIT sharees.
    dele = api_client.delete(reverse("v1:task-detail", args=[task.id]))
    assert dele.status_code == 403


def test_sharee_cannot_reshare(api_client, user, other_user):
    task = TaskFactory(owner=other_user)
    TaskShare.objects.create(task=task, user=user, permission=TaskShare.Permission.EDIT)
    api_client.force_authenticate(user=user)
    resp = api_client.post(
        reverse("v1:task-share", args=[task.id]),
        {"email": "someone@example.com"},
        format="json",
    )
    assert resp.status_code == 403
