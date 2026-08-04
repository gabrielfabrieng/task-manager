"""Root URL configuration. All API routes are versioned under /api/v1/."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_v1 = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.tasks.urls")),
    # OpenAPI schema + Swagger UI (self-documenting external API).
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # include() accepts (patterns, app_namespace); stubs mistype the tuple.
    path("api/v1/", include((api_v1, "v1"))),  # type: ignore[arg-type]
]
