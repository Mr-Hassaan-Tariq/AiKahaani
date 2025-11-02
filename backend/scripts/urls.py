# urls.py
from django.urls import include, path

from . import views
from . import test_views
from .views import *

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"admin/all-full-scripts", FullScriptAdminViewSet, basename="admin-all-full-scripts")


urlpatterns = [
    # Test endpoints for attachment features
    path("test/image/", test_views.test_image_analysis, name="test-image"),
    path("test/article/", test_views.test_article_scraping, name="test-article"),
    path("test/youtube/", test_views.test_youtube_transcript, name="test-youtube"),
    path("test/combined/", test_views.test_combined_attachments, name="test-combined"),
    
    # Config endpoint for UI
    path("config/", views.script_generator_config, name="script-config"),
    # Direct outline generation from user input
    path("outline/", views.generate_script_outline, name="generate-outline"),
    path(
        "outline/<uuid:uuid>/recreate/",
        views.recreate_script_outline,
        name="recreate-outline",
    ),
    path(
        "outline/<uuid:uuid>/script/",
        views.generate_full_script,
        name="generate-script",
    ),
    # Title generation endpoints
    path("titles/", include("scripts.titles.urls")),
    # Niches endpoint for users
    path("niches/", include("scripts.niches_urls")),
    # Unified listing API (replaces separate outline and script lists)
    path("generations/", views.GenerationsList.as_view(), name="generations-list"),
    # Individual CRUD (kept for backward compatibility)
    path("outlines/", views.ScriptOutlineListView.as_view(), name="outline-list"),
    path(
        "outlines/<uuid:uuid>/",
        views.ScriptOutlineDetailView.as_view(),
        name="outline-detail",
    ),
    path("", views.FullScriptListView.as_view(), name="full-script-list"),
    path(
        "<uuid:uuid>/", views.FullScriptDetailView.as_view(), name="full-script-detail"
    ),
    # Export endpoint
    path(
        "<uuid:uuid>/export/", views.ExportScriptView.as_view(), name="export-script"
    ),
]

# Include router URLs
urlpatterns += router.urls
