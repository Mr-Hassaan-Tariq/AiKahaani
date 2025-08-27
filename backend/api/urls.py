from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import health

urlpatterns = [
    path("health/", health.health_check, name="health_check"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/auth/", include("users.urls")),
    path("api/v1/users/", include("users.users_urls")),
    path("admin/", admin.site.urls),
]
