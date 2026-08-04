"""
Production settings — security hardened (OWASP A05: Security Misconfiguration).

DEBUG is forced off and secrets must come from the environment; there are no
insecure defaults here.
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY")  # no default: fail fast if unset
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# --- HTTPS / transport security ---
# Default on; can be disabled for an HTTP-only demo box that has no TLS yet.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- Cookies ---
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# --- Content / framing ---
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# CORS strictly by whitelist in production.
CORS_ALLOW_ALL_ORIGINS = False
