# notifications/serializers.py
from rest_framework import serializers

from .models import Notification, UserNotification


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

    def get_title(self, obj):
        return obj.title or (
            obj.global_notification.title if obj.global_notification else None
        )

    def get_message(self, obj):
        return obj.message or (
            obj.global_notification.message if obj.global_notification else None
        )
