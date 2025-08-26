from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import User


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
        fields = ("id", "email", "username", "fullname", "date_joined", "is_active")
        read_only_fields = ("id", "date_joined", "is_active")


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
