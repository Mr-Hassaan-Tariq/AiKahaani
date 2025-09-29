from rest_framework import serializers

from users.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Enhanced user serializer for admin panel with additional fields.
    """

    profile_picture = serializers.SerializerMethodField()
    roles_display = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    is_admin = serializers.SerializerMethodField()

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
            "is_active",
            "date_joined",
            "last_login",
            "roles",
            "roles_display",
            "is_admin",
            "has_used_trial",
        )
        read_only_fields = ("id", "date_joined", "last_login")

    def get_profile_picture(self, obj):
        """Get profile picture URL."""
        if not getattr(obj, "profile_picture", None):
            return None
        try:
            url = obj.profile_picture.url
        except Exception:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_roles_display(self, obj):
        """Get human-readable role names."""
        return [role.name for role in obj.roles.all()]

    def get_is_admin(self, obj):
        """Check if user is admin."""
        return obj.is_admin()


class AdminUserListSerializer(AdminUserSerializer):
    """
    Simplified serializer for user listing with only essential fields.
    """

    class Meta(AdminUserSerializer.Meta):
        fields = (
            "id",
            "email",
            "username",
            "fullname",
            "is_active",
            "date_joined",
            "roles_display",
            "is_admin",
            "is_email_verified",
        )
        read_only_fields = ("id", "date_joined")


class AdminUserDetailSerializer(AdminUserSerializer):
    """
    Detailed serializer for user detail view with all fields.
    """

    class Meta(AdminUserSerializer.Meta):
        fields = AdminUserSerializer.Meta.fields + (
            "email",
            "username",
            "fullname",
            "preferred_language",
        )


class AdminUserActionSerializer(serializers.Serializer):
    """
    Serializer for user management actions.
    """

    ACTION_CHOICES = [
        ("activate", "Activate"),
        ("deactivate", "Deactivate"),
        ("assign_role", "Assign Role"),
        ("remove_role", "Remove Role"),
    ]

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    role = serializers.CharField(required=False, allow_blank=True)


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user details by admin.
    """

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "fullname",
            "preferred_language",
            "is_active",
            "is_email_verified",
        )

    def validate_email(self, value):
        """Validate email uniqueness."""
        if self.instance and self.instance.email == value:
            return value

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate username uniqueness."""
        if self.instance and self.instance.username == value:
            return value

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value
