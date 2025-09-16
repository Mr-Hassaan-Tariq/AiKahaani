# urls.py
from django.urls import path

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
    # Outline CRUD
    path("outlines/", views.ScriptOutlineListView.as_view(), name="outline-list"),
    path(
        "outlines/<uuid:uuid>/",
        views.ScriptOutlineDetailView.as_view(),
        name="outline-detail",
    ),
    # Script CRUD
    path("scripts/", views.FullScriptListView.as_view(), name="full-script-list"),
    path(
        "scripts/<uuid:uuid>/",
        views.FullScriptDetailView.as_view(),
        name="full-script-detail",
    ),
    # Throttling test endpoint
    path("throttle-test/", views.ThrottleTestView.as_view(), name="throttle-test"),
]
