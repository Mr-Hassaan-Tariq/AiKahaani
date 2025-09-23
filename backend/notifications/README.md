# Notifications App

This app provides a comprehensive notification system for the TubeGenius platform.

## Models

- **Notification**: Global notifications that can be sent to all users
- **UserNotification**: User-specific notifications

## Helper Class

The `NotificationHelper` class provides convenient methods for creating notifications from other apps.

### Basic Usage

```python
from notifications.helpers import NotificationHelper
from notifications.choices import NotificationType, DeliveryChannel

# Create a simple user notification
notification = NotificationHelper.create_user_notification(
    user=request.user,
    title="Welcome!",
    message="Welcome to TubeGenius!",
    notification_type=NotificationType.ACCOUNT
)
```

### Specialized Methods

#### Script Notifications

```python
# Create a script completion notification
NotificationHelper.create_script_notification(
    user=user,
    script_title="My Awesome Video Script"
)
```

#### Subscription Notifications

```python
# Create a subscription update notification
NotificationHelper.create_subscription_notification(
    user=user,
    plan_name="Pro Plan",
    action="renewed"
)
```

#### Account Notifications

```python
# Create an account update notification
NotificationHelper.create_account_notification(
    user=user,
    action="updated",
    details="Your profile picture has been updated."
)
```

#### Feature Notifications

```python
# Create a feature announcement notification
NotificationHelper.create_feature_notification(
    user=user,
    feature_name="AI Voice Cloning"
)
```

#### Tips Notifications

```python
# Create a tips notification
NotificationHelper.create_tips_notification(
    user=user,
    tip_title="How to Write Engaging Video Titles"
)
```

#### Draft Reminders

```python
# Create a draft reminder
NotificationHelper.create_draft_reminder(
    user=user,
    draft_count=3
)
```

#### Community Notifications

```python
# Create a community update notification
NotificationHelper.create_community_notification(
    user=user,
    title="New Community Challenge",
    message="Join our latest video creation challenge!"
)
```

### Bulk Operations

#### Bulk User Notifications

```python
# Create notifications for multiple users
users = [user1, user2, user3]
notifications = NotificationHelper.create_bulk_user_notifications(
    users=users,
    title="System Maintenance",
    message="The system will be under maintenance tonight.",
    notification_type=NotificationType.ACCOUNT
)
```

#### Global Notifications

```python
# Create a global notification
global_notification = NotificationHelper.create_global_notification(
    title="New Feature Release",
    message="We've released a new AI-powered script generator!",
    notification_type=NotificationType.FEATURE
)
```

### Utility Methods

#### Mark Notifications as Read

```python
# Mark a specific notification as read
success = NotificationHelper.mark_notification_read(
    notification_id=123,
    user=request.user
)

# Mark all notifications as read for a user
count = NotificationHelper.mark_all_notifications_read(user=request.user)
```

## Usage in Other Apps

### In Scripts App

```python
# After generating a script
from notifications.helpers import NotificationHelper

def generate_script(request):
    # ... script generation logic ...

    # Create notification
    NotificationHelper.create_script_notification(
        user=request.user,
        script_title=script.title
    )
```

### In Payments App

```python
# After subscription update
from notifications.helpers import NotificationHelper

def handle_subscription_webhook(request):
    # ... webhook processing ...

    # Create notification
    NotificationHelper.create_subscription_notification(
        user=user,
        plan_name=plan.name,
        action="updated"
    )
```

### In Users App

```python
# After account update
from notifications.helpers import NotificationHelper

def update_profile(request):
    # ... profile update logic ...

    # Create notification
    NotificationHelper.create_account_notification(
        user=request.user,
        action="updated",
        details="Your profile has been successfully updated."
    )
```

## Notification Types

- `SCRIPT`: New Script Generated
- `ACCOUNT`: Account or Plan Changes
- `FEATURE`: Feature Updates
- `TIPS`: Tips & Content Inspiration
- `COMMUNITY`: Community or Affiliate Updates
- `SUBSCRIPTION`: Subscription Updates
- `DRAFTS`: Draft Reminders

## Delivery Channels

- `EMAIL`: Email notifications
- `IN_APP`: In-app notifications (default)
- `PUSH`: Web push notifications
