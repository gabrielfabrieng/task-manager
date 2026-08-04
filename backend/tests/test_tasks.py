"""Task CRUD, status toggle, filtering and pagination."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.tasks.models import Task
from tests.factories import CategoryFactory, TaskFactory

pytestmark = pytest.mark.django_db


def test_create_task_sets_owner(auth_client, user):
    resp = auth_client.post(
        reverse("v1:task-list"), {"title": "Buy milk"}, format="json"
    )
    assert resp.status_code == 201
    assert resp.data["owner"] == user.username
    assert Task.objects.get(id=resp.data["id"]).owner_id == user.id


def test_list_only_returns_own_tasks(auth_client, user, other_user):
    TaskFactory(owner=user, title="mine")
    TaskFactory(owner=other_user, title="theirs")
    resp = auth_client.get(reverse("v1:task-list"))
    titles = [t["title"] for t in resp.data["results"]]
    assert titles == ["mine"]


def test_toggle_status(auth_client, user):
    task = TaskFactory(owner=user)
    url = reverse("v1:task-status", args=[task.id])
    resp = auth_client.patch(url, {"done": True}, format="json")
    assert resp.status_code == 200
    assert resp.data["status"] == "done"
    assert resp.data["is_done"] is True


def test_cannot_assign_foreign_category(auth_client, user, other_user):
    foreign = CategoryFactory(owner=other_user)
    resp = auth_client.post(
        reverse("v1:task-list"),
        {"title": "x", "category": foreign.id},
        format="json",
    )
    assert resp.status_code == 400


def test_filter_by_status(auth_client, user):
    TaskFactory(owner=user, status=Task.Status.DONE)
    TaskFactory(owner=user, status=Task.Status.PENDING)
    resp = auth_client.get(reverse("v1:task-list"), {"status": "done"})
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["status"] == "done"


def test_pagination_metadata(auth_client, user):
    TaskFactory.create_batch(25, owner=user)
    resp = auth_client.get(reverse("v1:task-list"), {"page_size": 10})
    assert resp.data["count"] == 25
    assert len(resp.data["results"]) == 10
    assert resp.data["next"] is not None
