"""Custom user model.

We subclass AbstractUser (keeping username-based login) but enforce a unique
email, because task sharing resolves recipients by email address. Defining a
custom user model from the start is Django's recommended practice — swapping
later is painful.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("email address", unique=True)

    class Meta:
        db_table = "accounts_user"

    def __str__(self) -> str:
        return self.username
