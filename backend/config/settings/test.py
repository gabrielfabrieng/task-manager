"""Test settings — fast and hermetic."""

from .base import *  # noqa: F401,F403

# In-memory SQLite: fast, hermetic, no external Postgres needed for unit tests.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

# Run Celery tasks synchronously so tests need no worker/broker.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Fast password hashing for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# In-memory cache; no Redis needed in CI unit tests.
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Disable axes lockout during tests (we test auth logic, not rate limiting).
AXES_ENABLED = False

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
