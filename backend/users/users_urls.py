from django.urls import path

from users.views import (EmailVerificationAPIView,
                         UserDetailsUpdateAPIView)
from users.profile_views.views import (SettingsNotificationAPIView,
                                       SettingsPrivacyAPIView)

urlpatterns = [
    path("details/", UserDetailsUpdateAPIView.as_view(), name="user-details-update"),
    path(
        "verify-email/<uuid:token>",
        EmailVerificationAPIView.as_view(),
        name="verify-email",
    ),
    path("privacy", SettingsPrivacyAPIView.as_view(), name="user-settings-privacy"),
    path("notifications", SettingsNotificationAPIView.as_view(), name="user-settings-notifications"),
]
