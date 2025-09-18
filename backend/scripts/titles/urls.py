# titles/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("generate/", views.GenerateTitlesView.as_view(), name="generate-titles"),
    path(
        "optimize/", views.GenerateTitlesOptimizedView.as_view(), name="optimize-titles"
    ),
    path("tones/", views.TitleToneListView.as_view(), name="list-title-tones"),
]
