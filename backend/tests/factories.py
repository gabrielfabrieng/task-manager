"""factory_boy factories for test data."""

from __future__ import annotations

import factory
from django.contrib.auth import get_user_model

from apps.tasks.models import Category, Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "SuperSecret123")
        if create:
            self.save()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Category {n}")


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    owner = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Task {n}")
    description = "A task."
