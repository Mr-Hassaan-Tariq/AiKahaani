from django.urls import path

from scripts import niches_views

urlpatterns = [
    path("", niches_views.UserNicheListView.as_view(), name="user-niche-list"),
    path(
        "<int:pk>/",
        niches_views.UserNicheDetailView.as_view(),
        name="user-niche-detail",
    ),
]
