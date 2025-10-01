from rest_framework import serializers

from users.models import User

from .models import Niche, NichePacing, NicheTone


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


class NicheToneSerializer(serializers.ModelSerializer):
    """Serializer for NicheTone model."""

    class Meta:
        model = NicheTone
        fields = ["id", "name", "created", "modified"]
        read_only_fields = ["id", "created", "modified"]


class NichePacingSerializer(serializers.ModelSerializer):
    """Serializer for NichePacing model."""

    class Meta:
        model = NichePacing
        fields = ["id", "name", "created", "modified"]
        read_only_fields = ["id", "created", "modified"]


class NicheSerializer(serializers.ModelSerializer):
    """Serializer for Niche model with tone/pacing creation and deduplication."""

    class Meta:
        model = Niche
        fields = [
            "id",
            "admin",
            "title",
            "tagline",
            "thumbnail",
            "script_structure",
            "tone",
            "pacing",
            "top_channels",
            "best_for",
            "status",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "created", "modified"]

    def validate_tone(self, value):
        """Validate and deduplicate tone list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Tone must be a list.")
        # Remove duplicates and empty strings
        return list(set(filter(None, [str(item).strip() for item in value])))

    def validate_pacing(self, value):
        """Validate and deduplicate pacing list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Pacing must be a list.")
        # Remove duplicates and empty strings
        return list(set(filter(None, [str(item).strip() for item in value])))

    def validate_top_channels(self, value):
        """Validate and deduplicate top_channels list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Top channels must be a list.")
        # Remove duplicates and empty strings
        return list(set(filter(None, [str(item).strip() for item in value])))

    def validate_best_for(self, value):
        """Validate and deduplicate best_for list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Best for must be a list.")
        # Remove duplicates and empty strings
        return list(set(filter(None, [str(item).strip() for item in value])))

    def create(self, validated_data):
        """Create niche and handle tone/pacing creation."""
        tone_list = validated_data.pop("tone", [])
        pacing_list = validated_data.pop("pacing", [])

        # Create niche instance
        niche = Niche.objects.create(**validated_data)

        # Handle tone creation
        if tone_list:
            self._create_or_get_tones(tone_list)
            niche.tone = tone_list

        # Handle pacing creation
        if pacing_list:
            self._create_or_get_pacings(pacing_list)
            niche.pacing = pacing_list

        niche.save()
        return niche

    def update(self, instance, validated_data):
        """Update niche and handle tone/pacing creation."""
        tone_list = validated_data.pop("tone", None)
        pacing_list = validated_data.pop("pacing", None)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle tone creation/update
        if tone_list is not None:
            self._create_or_get_tones(tone_list)
            instance.tone = tone_list

        # Handle pacing creation/update
        if pacing_list is not None:
            self._create_or_get_pacings(pacing_list)
            instance.pacing = pacing_list

        instance.save()
        return instance

    def _create_or_get_tones(self, tone_list):
        """Create NicheTone instances for tones that don't exist."""
        for tone_name in tone_list:
            NicheTone.objects.get_or_create(name=tone_name)

    def _create_or_get_pacings(self, pacing_list):
        """Create NichePacing instances for pacings that don't exist."""
        for pacing_name in pacing_list:
            NichePacing.objects.get_or_create(name=pacing_name)
