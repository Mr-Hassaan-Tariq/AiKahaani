from django.urls import path

from users.views import (
    EmailVerificationAPIView,
    UserDetailsUpdateAPIView,
)

urlpatterns = [
    path("details/", UserDetailsUpdateAPIView.as_view(), name="user-details-update"),
    path(
        "verify-email/<uuid:token>",
        EmailVerificationAPIView.as_view(),
        name="verify-email",
    ),
]
