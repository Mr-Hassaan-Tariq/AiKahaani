from django.db import models


class NotificationType(models.TextChoices):
    SCRIPT = "script", "New Script Generated"
    ACCOUNT = "account", "Account or Plan Changes"
    FEATURE = "feature", "Feature Updates"
    TIPS = "tips", "Tips & Content Inspiration"
    COMMUNITY = "community", "Community or Affiliate Updates"
    SUBSCRIPTION = "subscription", "Subscription Updates"
    DRAFTS = "drafts", "Draft Reminders"
    TITLE = "title", "Title Optimizer"


class DeliveryChannel(models.TextChoices):
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In-App"
    PUSH = "push", "Web Push"
