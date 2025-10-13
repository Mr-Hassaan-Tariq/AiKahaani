from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from scripts import views

from . import health

urlpatterns = [
    path(
        "api/file/<uuid:uuid>/export/",
        views.ExportScriptView.as_view(),
        name="export-script",
    ),
    path("health/", health.health_check, name="health_check"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/auth/", include("users.urls")),
    path("api/v1/users/", include("users.users_urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/scripts/", include("scripts.urls")),
    path("admin/", admin.site.urls),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/admin/", include("admins.urls")),
    # dj-stripe webhook endpoint sadf
    path("webhooks/stripe/", include("djstripe.urls", namespace="djstripe-webhooks")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
