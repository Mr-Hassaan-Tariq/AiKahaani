from typing import List, Union

from django.contrib.auth import get_user_model
from django.db import transaction

from notifications.choices import DeliveryChannel, NotificationType
from notifications.models import Notification, UserNotification

User = get_user_model()


class NotificationHelper:
    """
    Helper class for creating notifications from other apps.
    Provides convenient methods for creating user-specific and global notifications.
    """

    @staticmethod
    def create_user_notification(
        user: User,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SCRIPT,
        delivery_channel: DeliveryChannel = DeliveryChannel.IN_APP,
    ) -> UserNotification:
        return UserNotification.objects.create(
            user=user,
            title=title,
            message=message,
        )

    @staticmethod
    def create_global_notification(
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.FEATURE,
        delivery_channel: DeliveryChannel = DeliveryChannel.IN_APP,
    ) -> Notification:
        """
        Create a global notification that can be sent to all users.

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification (default: FEATURE)
            delivery_channel: Delivery channel (default: IN_APP)

        Returns:
            Notification instance
        """
        return Notification.objects.create(
            title=title,
            message=message,
            type=notification_type,
            delivery_channel=delivery_channel,
        )

    @staticmethod
    def create_bulk_user_notifications(
        users: List[Union[User, int]],
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SCRIPT,
        delivery_channel: DeliveryChannel = DeliveryChannel.IN_APP,
        read: bool = False,
    ) -> List[UserNotification]:
        """
        Create notifications for multiple users in bulk.

        Args:
            users: List of User instances or user IDs
            title: Notification title
            message: Notification message
            notification_type: Type of notification (default: SCRIPT)
            delivery_channel: Delivery channel (default: IN_APP)
            read: Whether the notifications are read (default: False)

        Returns:
            List of UserNotification instances
        """
        # Convert user IDs to User instances if needed
        user_objects = []
        for user in users:
            if isinstance(user, int):
                user_objects.append(User.objects.get(id=user))
            else:
                user_objects.append(user)

        # Create notifications in bulk
        notifications = []
        with transaction.atomic():
            for user in user_objects:
                notification = UserNotification.objects.create(
                    user=user, title=title, message=message, read=read
                )
                notifications.append(notification)

        return notifications
