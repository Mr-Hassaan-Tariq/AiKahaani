from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .choices import LanguageChoices
from .models import User, Settings


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
            "modified"
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
            "modified"
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
