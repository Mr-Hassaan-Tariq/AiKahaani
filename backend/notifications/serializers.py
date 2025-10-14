# notifications/serializers.py
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Notification, UserNotification


class MarkNotificationReadResponseSerializer(serializers.Serializer):
    """Serializer for mark notification read response"""

    detail = serializers.CharField()


class MarkAllNotificationsReadResponseSerializer(serializers.Serializer):
    """Serializer for mark all notifications read response"""

    detail = serializers.CharField()
    marked_count = serializers.IntegerField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "created_at", "metadata"]


class UserNotificationSerializer(serializers.ModelSerializer):
    global_notification = NotificationSerializer(read_only=True)
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "title",
            "global_notification",
            "message",
            "read",
            "created_at",
            "metadata",
        ]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_title(self, obj):
        return obj.title or (
            obj.global_notification.title if obj.global_notification else None
        )

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_message(self, obj):
        return obj.message or (
            obj.global_notification.message if obj.global_notification else None
        )
