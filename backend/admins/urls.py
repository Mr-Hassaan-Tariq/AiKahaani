from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

# Create router for viewset routes
router = DefaultRouter()
router.register(r"users", views.AdminUserListViewSet, basename="admin-users")
router.register(r"niches", views.NicheViewSet, basename="admin-niches")
router.register(r"niche-tones", views.NicheToneViewSet, basename="admin-niche-tones")
router.register(
    r"niche-pacings", views.NichePacingViewSet, basename="admin-niche-pacings"
)

urlpatterns = [
    # Statistics endpoint
    path("user-stats/", views.UserStatsView.as_view(), name="user-stats"),
]

# Include router URLs
urlpatterns += router.urls
