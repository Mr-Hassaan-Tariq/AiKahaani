from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import LoginStatsView

from . import views

# Create router for viewset routes
router = DefaultRouter()
router.register(r"users", views.AdminUserListViewSet, basename="admin-users")
router.register(r"niches", views.NicheViewSet, basename="admin-niches")
router.register(r"niche-tones", views.NicheToneViewSet, basename="admin-niche-tones")
router.register(
    r"niche-pacings", views.NichePacingViewSet, basename="admin-niche-pacings"
)

# IMPORTANT: Define specific paths BEFORE router URLs
urlpatterns = [
    # Statistics endpoint
    path("user-stats/", views.UserStatsView.as_view(), name="user-stats"),
    path("admin-stats/", views.StatisticsAPIView.as_view(), name="statistics-api"),
    # Users report endpoints
    path("users-report/", views.UsersReportView.as_view(), name="users-report"),
    path(
        "users-report/export/",
        views.UsersReportExportView.as_view(),
        name="users-report-export",
    ),
    # Conversion funnel endpoints
    path(
        "conversion-funnel/",
        views.UserConversionFunnelView.as_view(),
        name="conversion-funnel",
    ),
    path(
        "conversion-funnel/export/",
        views.UserConversionFunnelExportView.as_view(),
        name="conversion-funnel-export",
    ),
    # Login statistics endpoint
    path("login-stats/", LoginStatsView.as_view(), name="login-stats"),
]

# Include router URLs AFTER specific paths
urlpatterns += router.urls
