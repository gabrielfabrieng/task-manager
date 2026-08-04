"""Task/Category HTTP layer. Thin viewsets delegating rules to services."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.exceptions import PermissionDeniedError

from .filters import TaskFilter
from .models import Category, Task
from .permissions import IsOwner, IsTaskOwnerOrSharee
from .serializers import (
    CategorySerializer,
    SetStatusSerializer,
    ShareRequestSerializer,
    TaskSerializer,
    TaskShareSerializer,
)
from .services import set_status, share_task, tasks_visible_to, unshare_task


@extend_schema(tags=["categories"])
class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD for the current user's categories."""

    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        # Scope by owner: a user never sees others' categories.
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(owner=self.request.user)


@extend_schema(tags=["tasks"])
class TaskViewSet(viewsets.ModelViewSet):
    """CRUD + sharing for tasks the user owns or that were shared with them."""

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskOwnerOrSharee]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "title", "status"]

    def get_queryset(self):
        # Queryset scoping is the first line of BOLA defence.
        return tasks_visible_to(self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(owner=self.request.user)

    def _require_owner(self, task: Task) -> None:
        if task.owner_id != self.request.user.id:
            raise PermissionDeniedError("Only the owner can manage sharing.")

    @extend_schema(request=SetStatusSerializer, responses=TaskSerializer)
    @action(detail=True, methods=["patch"])
    def status(self, request: Request, pk=None) -> Response:
        """PATCH /tasks/{id}/status/ — mark done / not done (requirement f)."""
        task = self.get_object()
        serializer = SetStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = set_status(task=task, done=serializer.validated_data["done"])
        return Response(TaskSerializer(task, context=self.get_serializer_context()).data)

    @extend_schema(request=ShareRequestSerializer, responses=TaskShareSerializer)
    @action(detail=True, methods=["post"])
    def share(self, request: Request, pk=None) -> Response:
        """POST /tasks/{id}/share/ — share with another user by e-mail."""
        task = self.get_object()
        self._require_owner(task)
        serializer = ShareRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        share = share_task(
            task=task,
            recipient_email=serializer.validated_data["email"],
            permission=serializer.validated_data["permission"],
        )
        return Response(TaskShareSerializer(share).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["delete"], url_path="share/(?P<user_id>[0-9]+)")
    def unshare(self, request: Request, pk=None, user_id=None) -> Response:
        """DELETE /tasks/{id}/share/{user_id}/ — revoke a share."""
        task = self.get_object()
        self._require_owner(task)
        unshare_task(task=task, user_id=int(user_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
