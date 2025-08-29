from django.urls import path

from users.views import (
    GoogleLoginAPIView,
    LogoutAPIView,
    MagicLinkLoginAPIView,
    MagicLinkVerifyAPIView,
    SignupView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("google/", GoogleLoginAPIView.as_view(), name="google-login"),
    path("magic-link/", MagicLinkLoginAPIView.as_view(), name="magic-link-login"),
    path(
        "magic-link/verify/", MagicLinkVerifyAPIView.as_view(), name="magic-link-verify"
    ),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
