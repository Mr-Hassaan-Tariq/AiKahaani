from django.urls import path

from users.views import (
    AdminLoginView,
    GoogleLoginAPIView,
    LogoutAPIView,
    MagicLinkLoginAPIView,
    MagicLinkVerifyAPIView,
    RefreshTokenView,
    SignupView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("google/", GoogleLoginAPIView.as_view(), name="google-login"),
    path("magic-link/", MagicLinkLoginAPIView.as_view(), name="magic-link-login"),
    path(
        "magic-link/verify/", MagicLinkVerifyAPIView.as_view(), name="magic-link-verify"
    ),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh-token"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
