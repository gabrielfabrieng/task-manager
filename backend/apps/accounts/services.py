"""Account business logic.

Kept out of serializers/views so it is reusable and unit-testable without HTTP.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.common.exceptions import ConflictError

if TYPE_CHECKING:
    from .models import User

UserModel = get_user_model()


def register_user(*, username: str, email: str, password: str) -> "User":
    """Create a user with a properly hashed password.

    Password strength is validated by the serializer (Django validators) before
    this is called; here we only persist and guard uniqueness at the DB level.
    """
    try:
        user = UserModel(username=username, email=email)
        user.set_password(password)  # Argon2 hashing
        user.full_clean(exclude=["password"])
        user.save()
    except IntegrityError as exc:
        raise ConflictError("Username or email already in use.") from exc
    return user
