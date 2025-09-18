# urls.py
from django.urls import include, path

from . import views

urlpatterns = [
    # Config endpoint for UI
    path("config/", views.script_generator_config, name="script-config"),
    # Direct outline generation from user input
    path("outline/", views.generate_script_outline, name="generate-outline"),
    path(
        "outline/<uuid:outline_uuid>/script/",
        views.generate_full_script,
        name="generate-script",
    ),
    # Title generation endpoints
    path("titles/", include("scripts.titles.urls")),
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
]
