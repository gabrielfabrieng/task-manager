"""
Domain exceptions and a DRF exception handler that maps them to HTTP.

Keeping business errors as plain exceptions lets the service layer stay
framework-agnostic: services raise DomainError, the handler translates it.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class DomainError(Exception):
    """Base class for expected, business-rule violations."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str = "Invalid request."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class PermissionDeniedError(DomainError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."


class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflicting request."


def handler(exc, context):
    """DRF exception handler: translate DomainError, defer the rest to DRF."""
    if isinstance(exc, DomainError):
        return Response({"detail": exc.detail}, status=exc.status_code)
    return drf_exception_handler(exc, context)
