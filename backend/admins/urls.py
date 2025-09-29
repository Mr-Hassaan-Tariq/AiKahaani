from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

# Create router for viewset routes
router = DefaultRouter()
router.register(r"users", views.AdminUserListViewSet, basename="admin-users")

urlpatterns = [
    # Statistics endpoint
    path("user-stats/", views.UserStatsView.as_view(), name="user-stats"),
]

# Include router URLs
urlpatterns += router.urls
