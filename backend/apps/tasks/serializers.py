"""Task/Category (de)serialization and input validation."""

from __future__ import annotations

from rest_framework import serializers

from .models import Category, Task, TaskShare


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "color", "created_at")
        read_only_fields = ("id", "created_at")


class TaskShareSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = TaskShare
        fields = ("id", "user", "permission", "created_at")
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)
    shares = TaskShareSerializer(many=True, read_only=True)
    is_done = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "owner",
            "title",
            "description",
            "status",
            "is_done",
            "category",
            "due_date",
            "shares",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "shares", "created_at", "updated_at")

    def validate_category(self, category: Category | None) -> Category | None:
        """A user may only assign their OWN categories to a task (BOLA guard)."""
        if category is None:
            return None
        request = self.context["request"]
        if category.owner_id != request.user.id:
            raise serializers.ValidationError("Category does not belong to you.")
        return category


class ShareRequestSerializer(serializers.Serializer):
    """Input for POST /tasks/{id}/share/."""

    email = serializers.EmailField()
    permission = serializers.ChoiceField(
        choices=TaskShare.Permission.choices,
        default=TaskShare.Permission.VIEW,
    )


class SetStatusSerializer(serializers.Serializer):
    """Input for PATCH /tasks/{id}/status/."""

    done = serializers.BooleanField()
