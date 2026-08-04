"""Local development settings."""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Convenience: let the browsable API and Swagger be reachable without CORS pain.
CORS_ALLOW_ALL_ORIGINS = env("DJANGO_DEBUG", default=True)
