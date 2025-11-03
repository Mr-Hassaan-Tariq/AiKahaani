from django.urls import path

from . import views

app_name = "affiliates"

urlpatterns = [
    # Track referral click (no auth required)
    # Frontend calls this when user lands with ?ref=ABC123
    path(
        "click/",
        views.track_referral_click,
        name="track-click"
    ),
]
