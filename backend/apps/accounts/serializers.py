"""Account (de)serialization and input validation."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (never exposes the password)."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=10, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def validate_password(self, value: str) -> str:
        # Run Django's configured password validators (length, common, numeric...).
        validate_password(value)
        return value
