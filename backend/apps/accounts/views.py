"""Account HTTP endpoints. Views stay thin: validate -> call service -> serialize."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer
from .services import register_user


@extend_schema(tags=["auth"])
class RegisterView(generics.CreateAPIView):
    """POST /auth/register/ — open endpoint to create an account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=201)


@extend_schema(tags=["auth"])
class MeView(generics.RetrieveAPIView):
    """GET /auth/me/ — the authenticated user's profile."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
