# titles/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from scripts.titles.views import *

router = DefaultRouter()
router.register(r"admin/all-titles", UserTitlesAdminViewSet, basename="admin-all-titles")


urlpatterns = [
    path("generate/", views.GenerateTitlesView.as_view(), name="generate-titles"),
    path(
        "optimize/", views.GenerateTitlesOptimizedView.as_view(), name="optimize-titles"
    ),
    path("tones/", views.TitleToneListView.as_view(), name="list-title-tones"),
    path("users/", views.UserTitlesListView.as_view(), name="user-all-titles-list"),
]

# Include router URLs
urlpatterns += router.urls
