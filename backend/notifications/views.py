from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import MethodSpecificThrottleMixin
from notifications.models import UserNotification
from notifications.serializers import UserNotificationSerializer


class UserNotificationListView(MethodSpecificThrottleMixin, generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Notifications"],
        summary="Get user notifications",
        description="""
            Retrieve a list of notifications for the authenticated user.

            - Results are ordered by newest first (`created_at`).
            - Supports optional filtering by read/unread state.
            """,
        parameters=[
            OpenApiParameter(
                name="read",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter notifications by read state. "
                "`true` = only read, `false` = only unread.",
            )
        ],
        responses={200: UserNotificationSerializer(many=True)},
    )
    def get_queryset(self):
        user = self.request.user
        queryset = UserNotification.objects.filter(user=user).order_by("-created_at")

        # Optional filtering by read/unread
        read = self.request.query_params.get("read")
        if read is not None:
            queryset = queryset.filter(read=(read.lower() == "true"))

        return queryset


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Notifications"],
        summary="Mark a notification as read",
        description="""
            Mark a single user notification as read.

            - Requires authentication.
            - Returns `404` if the notification does not exist or does not belong to the user.
            """,
        responses={
            200: OpenApiParameter(
                name="detail",
                description="Confirmation message",
                required=True,
                type=str,
            ),
            404: OpenApiParameter(
                name="detail",
                description="Error message if notification not found",
                required=True,
                type=str,
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
