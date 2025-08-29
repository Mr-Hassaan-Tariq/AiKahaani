from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Settings
from users.serializers import SettingsNotificationSerializer, SettingsPrivacySerializer


@extend_schema(
    operation_id="settings_notification_update",
    summary="Update notification settings",
    description=(
        "Authenticated endpoint to update the current user's notification settings. "
        "Allows the user to manage in-app notifications, email notifications, web push notifications, "
        "and other related preferences."
    ),
    request=SettingsNotificationSerializer,
    responses={
        200: OpenApiResponse(
            description="Notification settings updated successfully",
            response=SettingsNotificationSerializer,
            examples=[
                OpenApiExample(
                    "Update Success",
                    value={
                        "user": 1,
                        "in_app_notifications": True,
                        "email_notifications": False,
                        "web_push_notifications": True,
                        "new_script_generated": False,
                        "account_or_plan_changes": True,
                        "tips_content_inspiration": False,
                        "feature_updates": True,
                        "community_affiliate_updates": False,
                        "created": "2025-08-27T00:00:00Z",
                        "modified": "2025-08-27T00:00:00Z",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            description="Validation error",
            examples=[
                OpenApiExample(
                    "Invalid Notification Setting",
                    value={"email_notifications": ["This field is required."]},
                    response_only=True,
                ),
            ],
        ),
    },
    tags=["Settings"],
)
class SettingsNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings, created = Settings.objects.get_or_create(user=request.user)
        serializer = SettingsNotificationSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        settings, created = Settings.objects.get_or_create(user=request.user)
        serializer = SettingsNotificationSerializer(
            settings, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(
    operation_id="settings_privacy_update",
    summary="Update privacy settings",
    description=(
        "Authenticated endpoint to update the current user's privacy settings. "
        "Allows the user to manage email preferences, anonymized data usage, and other privacy-related options."
    ),
    request=SettingsPrivacySerializer,
    responses={
        200: OpenApiResponse(
            description="Privacy settings updated successfully",
            response=SettingsPrivacySerializer,
            examples=[
                OpenApiExample(
                    "Update Success",
                    value={
                        "user": 1,
                        "allow_product_update_emails": True,
                        "allow_anonymized_data_usage": False,
                        "created": "2025-08-27T00:00:00Z",
                        "modified": "2025-08-27T00:00:00Z",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            description="Validation error",
            examples=[
                OpenApiExample(
                    "Invalid Privacy Setting",
                    value={"allow_anonymized_data_usage": ["This field is required."]},
                    response_only=True,
                ),
            ],
        ),
    },
    tags=["Settings"],
)
class SettingsPrivacyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings, created = Settings.objects.get_or_create(user=request.user)
        serializer = SettingsPrivacySerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        settings, created = Settings.objects.get_or_create(user=request.user)
        serializer = SettingsPrivacySerializer(
            settings, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
