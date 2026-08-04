"""Auth flow tests: registration, JWT login, weak-password rejection."""

from __future__ import annotations

import pytest
from django.urls import reverse

from tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_register_creates_user(api_client):
    resp = api_client.post(
        reverse("v1:register"),
        {"username": "alice", "email": "alice@example.com", "password": "StrongPass123"},
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["username"] == "alice"
    assert "password" not in resp.data


def test_register_rejects_weak_password(api_client):
    resp = api_client.post(
        reverse("v1:register"),
        {"username": "bob", "email": "bob@example.com", "password": "123"},
        format="json",
    )
    assert resp.status_code == 400
    assert "password" in resp.data


def test_login_returns_jwt_pair(api_client):
    user = UserFactory(username="carol")
    user.set_password("StrongPass123")
    user.save()
    resp = api_client.post(
        reverse("v1:token_obtain_pair"),
        {"username": "carol", "password": "StrongPass123"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data and "refresh" in resp.data


def test_me_requires_auth(api_client):
    assert api_client.get(reverse("v1:me")).status_code == 401
