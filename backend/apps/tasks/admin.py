from django.contrib import admin

from .models import Category, Task, TaskShare


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "color", "created_at")
    search_fields = ("name",)


class TaskShareInline(admin.TabularInline):
    model = TaskShare
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "category", "due_date")
    list_filter = ("status",)
    search_fields = ("title", "description")
    inlines = [TaskShareInline]
