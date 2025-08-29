import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from users.choices import LanguageChoices


class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=150, unique=True)
    fullname = models.CharField(_("full name"), max_length=255, blank=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH,
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )
    is_email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email


class MagicLinkToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return self.expires_at > timezone.now()


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return self.expires_at > timezone.now()


class Settings(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allow_product_update_emails = models.BooleanField(default=False)
    allow_anonymized_data_usage = models.BooleanField(default=False)
    in_app_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=False)
    web_push_notifications = models.BooleanField(default=False)
    new_script_generated = models.BooleanField(default=False)
    account_or_plan_changes = models.BooleanField(default=False)
    tips_content_inspiration = models.BooleanField(default=False)
    feature_updates = models.BooleanField(default=False)
    community_affiliate_updates = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("user settings")
        verbose_name_plural = _("user settings")

    def __str__(self):
        return f"Settings for {self.user.email}"


class BlacklistedAccessToken(TimeStampedModel):
    """
    Stores JTIs of access tokens that have been explicitly invalidated before
    their natural expiration, enabling immediate logout for access tokens.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blacklisted_access_tokens"
    )
    jti = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["jti"]),
            models.Index(fields=["expires_at"]),
        ]
        verbose_name = _("blacklisted access token")
        verbose_name_plural = _("blacklisted access tokens")

    def __str__(self):
        return f"BlacklistedAccessToken(jti={self.jti})"
