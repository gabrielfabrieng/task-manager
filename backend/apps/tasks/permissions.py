"""
Object-level authorization (OWASP API1 — Broken Object Level Authorization).

Every object access is checked against the requesting user. We never trust an
ID from the URL alone: the queryset is scoped per-user AND these permissions
re-check ownership on the resolved object.
"""

from __future__ import annotations

from rest_framework import permissions
from rest_framework.request import Request

from .models import Task, TaskShare


class IsOwner(permissions.BasePermission):
    """Only the object's owner may access it (used for Category)."""

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return obj.owner_id == request.user.id


class IsTaskOwnerOrSharee(permissions.BasePermission):
    """
    Task access rules:

    - Owner: full access (read, write, delete, share).
    - Shared with EDIT: read + update (not delete, not re-share).
    - Shared with VIEW: read only.
    - Everyone else: denied (404 via queryset scoping, 403 here as defence-in-depth).
    """

    def has_object_permission(self, request: Request, view, obj: Task) -> bool:
        if obj.owner_id == request.user.id:
            return True

        share = obj.shares.filter(user_id=request.user.id).first()
        if share is None:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        # Non-safe method: destructive/administrative actions stay owner-only.
        if view.action in {"destroy", "share", "unshare"}:
            return False

        return share.permission == TaskShare.Permission.EDIT
