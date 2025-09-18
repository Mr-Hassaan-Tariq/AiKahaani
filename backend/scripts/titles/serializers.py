# titles/serializers.py
from rest_framework import serializers

from scripts.models import TitleTone


class TitleToneSerializer(serializers.ModelSerializer):
    """
    Serializer for TitleTone model to list available tones
    """

    class Meta:
        model = TitleTone
        fields = ["id", "name", "created", "modified"]
        read_only_fields = ["id", "created", "modified"]


class GenerateTitlesRequestSerializer(serializers.Serializer):
    """
    Serializer for title generation request
    """

    prompt = serializers.CharField(
        max_length=2000,
        min_length=30,
        help_text="Description or context for the video title generation (30-2000 characters)",
    )
    title_count = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=30,
        help_text="Number of title variations to generate (1-30, default: 10)",
    )
    tones = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
        max_length=3,
        help_text="List of tones/styles for title generation (max 3). Examples: ['Controversial', 'Shocking', 'Persuasive']",
    )

    def validate_prompt(self, value):
        """Validate prompt content"""
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Prompt cannot be empty or only whitespace."
            )

        # Check for minimum meaningful content
        if len(value.split()) < 3:
            raise serializers.ValidationError(
                "Prompt must contain at least 5 words for meaningful title generation."
            )

        return value

    def validate_tones(self, value):
        """Validate tones list and check for contradicting combinations"""
        if value is None:
            return []

        # Get valid tones from the database
        valid_tone_objects = TitleTone.objects.all()
        valid_tones = [tone.name.lower() for tone in valid_tone_objects]
        valid_tones_display = [tone.name for tone in valid_tone_objects]

        # Clean and validate each tone
        cleaned_tones = []
        for tone in value:
            tone_clean = tone.strip().lower()
            if tone_clean and tone_clean in valid_tones:
                # Find the proper case version from database
                proper_case = next(
                    t.name for t in valid_tone_objects if t.name.lower() == tone_clean
                )
                cleaned_tones.append(proper_case)
            elif tone_clean:
                raise serializers.ValidationError(
                    f"Invalid tone '{tone}'. Valid options: {', '.join(valid_tones_display)}"
                )

        # Remove duplicates while preserving order
        seen = set()
        unique_tones = []
        for tone in cleaned_tones:
            if tone.lower() not in seen:
                seen.add(tone.lower())
                unique_tones.append(tone)

        # Check for contradicting tone combinations
        self._validate_tone_contradictions(unique_tones)

        return unique_tones

    def _validate_tone_contradictions(self, tones):
        """Check for contradicting tone combinations"""
        if len(tones) < 2:
            return  # No conflicts possible with less than 2 tones

        tone_set = {tone.lower() for tone in tones}

        # Define contradicting tone groups
        contradictions = [
            {
                "group": {"neutral", "controversial"},
                "message": "Neutral and Controversial tones contradict each other. Neutral aims for objectivity while Controversial seeks to provoke debate.",
            },
            {
                "group": {"neutral", "shocking"},
                "message": "Neutral and Shocking tones contradict each other. Neutral uses calm language while Shocking uses extreme statements.",
            },
            {
                "group": {"neutral", "dramatic"},
                "message": "Neutral and Dramatic tones contradict each other. Neutral avoids intensity while Dramatic amplifies emotional impact.",
            },
            {
                "group": {"neutral", "sarcastic"},
                "message": "Neutral and Sarcastic tones contradict each other. Neutral maintains objectivity while Sarcastic uses irony and mockery.",
            },
            {
                "group": {"sarcastic", "persuasive"},
                "message": "Sarcastic and Persuasive tones can contradict each other. Sarcasm may undermine the sincere convincing nature of Persuasive content.",
            },
            {
                "group": {"witty", "dramatic"},
                "message": "Witty and Dramatic tones may contradict each other. Wit lightens the mood while Drama intensifies emotions.",
            },
            {
                "group": {"mysterious", "shocking"},
                "message": "Mysterious and Shocking tones can contradict each other. Mystery builds intrigue subtly while Shocking reveals dramatically.",
            },
        ]

        # Check for any contradictions
        for contradiction in contradictions:
            conflicting_group = contradiction["group"]
            if conflicting_group.issubset(tone_set):
                conflicting_tones = [
                    tone.title() for tone in conflicting_group if tone in tone_set
                ]
                raise serializers.ValidationError(
                    f"Contradicting tones detected: {' and '.join(conflicting_tones)}. "
                    f"{contradiction['message']}"
                )

        # Check for too many intense tones that might overwhelm
        intense_tones = {"controversial", "shocking", "dramatic"}
        intense_count = len(intense_tones.intersection(tone_set))

        if intense_count >= 3:
            intense_found = [
                tone.title() for tone in tones if tone.lower() in intense_tones
            ]
            raise serializers.ValidationError(
                f"Too many intense tones selected: {', '.join(intense_found)}. "
                "Using multiple intense tones (Controversial, Shocking, Dramatic) together may create "
                "overly aggressive titles. Consider using at most 2 intense tones."
            )

        # Check for conflicting question styles
        question_styles = {"question-based", "sarcastic"}
        if question_styles.issubset(tone_set):
            raise serializers.ValidationError(
                "Question-based and Sarcastic tones together may create confusing titles. "
                "Sarcastic questions can be unclear to audiences unfamiliar with the context."
            )


class GenerateTitlesOptimizedRequestSerializer(GenerateTitlesRequestSerializer):
    """
    Serializer for optimized title generation request
    Inherits from GenerateTitlesRequestSerializer and adds script/user_title fields
    """

    script = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="UUID of the script to optimize titles for (optional)",
    )
    user_title = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="User provided title to optimize (required if script not provided)",
    )

    # Override defaults for optimization use case
    title_count = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=15,
        help_text="Number of optimized title variations to generate (1-15, default: 5)",
    )
    prompt = serializers.CharField(
        max_length=2000,
        min_length=10,
        help_text="Additional context or instructions for optimization (10-2000 characters)",
    )

    def validate(self, data):
        """
        First run parent validation, then add our custom validation
        """
        # Run parent validation first
        data = super().validate(data)

        # Add custom validation for script/user_title
        script = data.get("script")
        user_title = data.get("user_title")

        if not script and not user_title:
            raise serializers.ValidationError(
                "Either 'script' (UUID) or 'user_title' must be provided."
            )

        if script and user_title:
            raise serializers.ValidationError(
                "Provide either 'script' or 'user_title', not both."
            )

        return data

    def validate_script(self, value):
        """
        Validate script exists and belongs to the authenticated user
        """
        if value is None:
            return value

        from scripts.models import Script

        # Get the user from the request context
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")

        try:
            script = Script.objects.get(uuid=value, user=request.user)
            return script
        except Script.DoesNotExist:
            raise serializers.ValidationError(
                "Script not found or you don't have permission to access it."
            ) from None

    def validate_user_title(self, value):
        """
        Validate user provided title
        """
        if value is not None:
            value = value.strip()
            if not value:
                raise serializers.ValidationError(
                    "User title cannot be empty or only whitespace."
                )

            if len(value.split()) < 2:
                raise serializers.ValidationError(
                    "User title must contain at least 2 words."
                )

        return value

    def validate_prompt(self, value):
        """
        Override parent validation with different requirements for optimization
        """
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Prompt cannot be empty or only whitespace."
            )

        # Optimization prompts can be shorter than generation prompts
        if len(value.split()) < 3:
            raise serializers.ValidationError(
                "Prompt must contain at least 3 words for meaningful optimization."
            )

        return value


class GenerateTitlesResponseSerializer(serializers.Serializer):
    """
    Serializer for title generation response
    """

    titles = serializers.ListField(
        child=serializers.CharField(), help_text="List of generated YouTube titles"
    )
    metadata = serializers.DictField(
        help_text="Generation metadata including token usage and timing"
    )
    message = serializers.CharField(help_text="Success message")
