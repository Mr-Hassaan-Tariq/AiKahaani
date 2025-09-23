from django.contrib.auth import get_user_model
from django.db import models

from notifications.choices import DeliveryChannel, NotificationType

User = get_user_model()


class Notification(models.Model):
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SCRIPT,
    )
    delivery_channel = models.CharField(
        max_length=20,
        choices=DeliveryChannel.choices,
        default=DeliveryChannel.IN_APP,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    global_notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif for {self.user.email} - {self.title or self.global_notification.title}"
