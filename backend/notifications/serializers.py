# notifications/serializers.py
from rest_framework import serializers

from .models import UserNotification


class UserNotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = ["id", "title", "message", "read", "created_at"]

    def get_title(self, obj):
        return obj.title or (
            obj.global_notification.title if obj.global_notification else None
        )

    def get_message(self, obj):
        return obj.message or (
            obj.global_notification.message if obj.global_notification else None
        )
