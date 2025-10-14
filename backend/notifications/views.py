from django.db import models
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import MethodSpecificThrottleMixin
from notifications.choices import NotificationType
from notifications.models import UserNotification
from notifications.serializers import (
    MarkAllNotificationsReadResponseSerializer,
    MarkNotificationReadResponseSerializer,
    UserNotificationSerializer,
)
from scripts.pagination import GenerationsLimitOffsetPagination


class UserNotificationListView(MethodSpecificThrottleMixin, generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = GenerationsLimitOffsetPagination

    @extend_schema(
        tags=["Notifications"],
        summary="List user notifications",
        description="""
            Retrieve paginated notifications for the authenticated user.

            - Requires authentication.
            - Returns notifications ordered by creation date (newest first).
            - Optional query parameter 'read' to filter by read/unread status.
            - Optional query parameter 'type' to filter by notification type.
            - Supports pagination with 'limit' and 'offset' parameters.
            """,
        parameters=[
            OpenApiParameter(
                name="read",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter notifications by read status (true/false)",
                required=False,
            ),
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=f"Filter notifications by type. Available types: {', '.join([choice[0] for choice in NotificationType.choices])}",
                required=False,
                enum=[choice[0] for choice in NotificationType.choices],
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of notifications to return per page (default: 20, max: 100)",
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of notifications to skip from the beginning (default: 0)",
                required=False,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserNotification.objects.none()
        user = self.request.user
        queryset = UserNotification.objects.filter(user=user).order_by("-created_at")

        # Optional filtering by read/unread
        read = self.request.query_params.get("read")
        if read is not None:
            queryset = queryset.filter(read=(read.lower() == "true"))

        # Optional filtering by notification type
        notification_type = self.request.query_params.get("type")
        if notification_type is not None:
            # Filter by UserNotification.type if it exists, otherwise by global_notification.type
            queryset = queryset.filter(
                models.Q(type=notification_type)
                | models.Q(
                    type__isnull=True, global_notification__type=notification_type
                )
            )

        return queryset


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MarkNotificationReadResponseSerializer

    @extend_schema(
        tags=["Notifications"],
        summary="Mark a notification as read",
        description="""
            Mark a single user notification as read.

            - Requires authentication.
            - Returns `404` if the notification does not exist or does not belong to the user.
            """,
        responses={
            200: OpenApiResponse(
                description="Notification marked as read successfully",
                response=MarkNotificationReadResponseSerializer,
            ),
            404: OpenApiResponse(
                description="Notification not found or access denied",
            ),
        },
    )
    def post(self, request, pk):
        try:
            notif = UserNotification.objects.get(id=pk, user=request.user)
            notif.read = True
            notif.save()
            return Response({"detail": "Notification marked as read."})
        except UserNotification.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class MarkAllNotificationsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MarkAllNotificationsReadResponseSerializer

    @extend_schema(
        tags=["Notifications"],
        summary="Mark all notifications as read",
        description="""
            Mark **all unread notifications** for the authenticated user as read.

            - Requires authentication.
            - Updates every `UserNotification` with `read=False` → `read=True`.
            """,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "All notifications marked as read.",
                    }
                },
            }
        },
    )
    def post(self, request):
        UserNotification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({"detail": "All notifications marked as read."})
