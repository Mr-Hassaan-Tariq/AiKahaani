from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .choices import LanguageChoices
from .models import Settings, User


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("email", "username", "fullname", "password", "password_confirm")
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e)) from e
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "fullname",
            "preferred_language",
            "profile_picture",
            "is_email_verified",
        )
        read_only_fields = ("id",)

    def get_profile_picture(self, obj):
        if not getattr(obj, "profile_picture", None):
            return None
        try:
            url = obj.profile_picture.url
        except Exception:
            return None
        request = self.context.get("request")
        # for now will change it after s3
        return request.build_absolute_uri(url) if request else url


class GoogleAuthInputSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class MagicLinkLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()


class MagicLinkVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        """Validate that the token is a properly formatted UUID"""
        import uuid

        try:
            # Try to parse as UUID to validate format
            uuid.UUID(value)
            return value
        except ValueError as e:
            raise serializers.ValidationError("Invalid token format.") from e


class UserDetailsUpdateSerializer(serializers.Serializer):
    fullName = serializers.CharField(required=False, allow_blank=True, max_length=255)
    username = serializers.CharField(required=False, max_length=150)
    emailAddress = serializers.EmailField(required=False)
    preferredLanguage = serializers.ChoiceField(
        required=False, choices=[choice.value for choice in LanguageChoices]
    )

    def validate_username(self, value):
        user = self.context["request"].user
        if (
            value
            and User.objects.exclude(pk=user.pk).filter(username__iexact=value).exists()
        ):
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_emailAddress(self, value):
        user = self.context["request"].user
        if (
            value
            and User.objects.exclude(pk=user.pk).filter(email__iexact=value).exists()
        ):
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update_user(self, user):
        data = self.validated_data
        if "fullName" in data:
            user.fullname = data["fullName"].strip()
        if "username" in data:
            user.username = data["username"].strip()
        if "preferredLanguage" in data:
            user.preferred_language = data["preferredLanguage"]

        user.save()
        return user


class SettingsNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = [
            "in_app_notifications",
            "email_notifications",
            "web_push_notifications",
            "new_script_generated",
            "account_or_plan_changes",
            "tips_content_inspiration",
            "feature_updates",
            "community_affiliate_updates",
            "created",
            "modified",
        ]
        read_only_fields = ["created", "modified"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SettingsPrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = [
            "allow_product_update_emails",
            "allow_anonymized_data_usage",
            "created",
            "modified",
        ]
        read_only_fields = ["created", "modified"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ---------------------------------------------------------------------------
# Response Serializers (for API documentation and explicit response schemas)
# ---------------------------------------------------------------------------


class UserBasicSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    username = serializers.CharField()
    fullname = serializers.CharField(allow_blank=True)


class MagicLinkLoginSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class MagicLinkVerifySuccessResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserBasicSerializer()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint. Requires refresh token to blacklist."""

    refresh = serializers.CharField(required=True, allow_blank=False)

    def validate_refresh(self, value):
        """Validate that the refresh token is not empty or only whitespace."""
        if not value or not value.strip():
            raise serializers.ValidationError("Refresh token is required.")
        return value.strip()


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ProfilePictureUploadSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField(required=True)

    def validate_profile_picture(self, value):
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError("Image size must be <= 5MB.")
        valid_content_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if (
            hasattr(value, "content_type")
            and value.content_type not in valid_content_types
        ):
            raise serializers.ValidationError(
                "Unsupported image type. Use JPEG, PNG, WEBP, or GIF."
            )
        return value


class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer for admin login with email and password.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """
        Validate email and password, and check if user has admin role.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate the user
        from django.contrib.auth import authenticate

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        # Check if user has admin role
        if not user.is_admin():
            raise serializers.ValidationError("Access denied. Admin role required.")

        attrs["user"] = user
        return attrs


class AdminLoginResponseSerializer(serializers.Serializer):
    """
    Response serializer for admin login.
    """

    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer()
    message = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for refresh token request.
    """

    refresh_token = serializers.CharField(required=True)

    def validate_refresh_token(self, value):
        """
        Validate the refresh token.
        """
        try:
            from rest_framework_simplejwt.tokens import RefreshToken

            token = RefreshToken(value)
            # This will raise an exception if the token is invalid
            token.verify()
            return value
        except Exception:
            raise serializers.ValidationError("Invalid refresh token.")


class RefreshTokenResponseSerializer(serializers.Serializer):
    """
    Response serializer for refresh token.
    """

    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    message = serializers.CharField()
