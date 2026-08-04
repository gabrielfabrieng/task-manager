"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user) -> APIClient:
    """API client authenticated as ``user`` via forced auth."""
    api_client.force_authenticate(user=user)
    return api_client
