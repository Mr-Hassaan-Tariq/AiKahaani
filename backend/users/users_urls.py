from django.urls import path

from users.profile_views.views import (
    SettingsNotificationAPIView,
    SettingsPrivacyAPIView,
)
from users.views import (
    EmailVerificationAPIView,
    UserDetailsUpdateAPIView,
    UserProfilePictureAPIView,
)

urlpatterns = [
    path("details/", UserDetailsUpdateAPIView.as_view(), name="user-details-update"),
    path(
        "profile-picture",
        UserProfilePictureAPIView.as_view(),
        name="user-profile-picture",
    ),
    path(
        "verify-email/<uuid:token>",
        EmailVerificationAPIView.as_view(),
        name="verify-email",
    ),
    path("privacy", SettingsPrivacyAPIView.as_view(), name="user-settings-privacy"),
    path(
        "notifications",
        SettingsNotificationAPIView.as_view(),
        name="user-settings-notifications",
    ),
]
