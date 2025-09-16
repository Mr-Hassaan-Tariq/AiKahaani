# serializers.py
from .models import Tone, TemplateStyle, ScriptOutline, FullScript

from rest_framework import serializers


class ToneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tone
        fields = ['id', 'name']


class TemplateStyleSerializer(serializers.ModelSerializer):
    word_range = serializers.SerializerMethodField()

    class Meta:
        model = TemplateStyle
        fields = ['id', 'name', 'min_length', 'max_length', 'duration', 'description', 'word_range']

    def get_word_range(self, obj):
        return f"~{obj.min_length}-{obj.max_length} words"


class ScriptOutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptOutline
        fields = [
            'uuid', 'title', 'outline_text', 'outline_data',
            'status', 'version', 'tokens_used', 'generation_time',
            'created', 'modified'
        ]
        read_only_fields = ['uuid', 'tokens_used', 'generation_time', 'version']


class ScriptOutlineUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptOutline
        fields = ['title', 'outline_text']


class FullScriptSerializer(serializers.ModelSerializer):
    outline_title = serializers.CharField(source='outline.title', read_only=True)

    class Meta:
        model = FullScript
        fields = [
            'uuid', 'title', 'content', 'sections', 'word_count',
            'estimated_duration', 'status', 'version', 'is_published',
            'tokens_used', 'generation_time', 'outline_title',
            'created', 'modified'
        ]
        read_only_fields = [
            'uuid', 'word_count', 'estimated_duration',
            'tokens_used', 'generation_time', 'version'
        ]


# Response serializers that reference the model serializers above
class ScriptGeneratorConfigResponseSerializer(serializers.Serializer):
    tones = ToneSerializer(many=True)
    template_styles = TemplateStyleSerializer(many=True)
    outline_length_range = serializers.DictField()
    script_length_range = serializers.DictField()


class GenerateOutlineRequestSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=2000)
    tone = serializers.IntegerField()
    template_style = serializers.IntegerField(required=False, allow_null=True)
    min_length = serializers.IntegerField(default=100, min_value=50, max_value=5000)
    max_length = serializers.IntegerField(default=1000, min_value=100, max_value=10000)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)


class GenerateOutlineResponseSerializer(serializers.Serializer):
    outline = ScriptOutlineSerializer()
    message = serializers.CharField()


class GenerateScriptRequestSerializer(serializers.Serializer):
    tone = serializers.CharField(default="Informative")
    template_style = serializers.CharField(default="medium")
    min_length = serializers.IntegerField(default=1000, min_value=500, max_value=10000)
    max_length = serializers.IntegerField(default=5000, min_value=1000, max_value=20000)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)


class GenerateScriptResponseSerializer(serializers.Serializer):
    script = FullScriptSerializer()
    message = serializers.CharField()


class UnifiedGenerationSerializer(serializers.Serializer):
    """
    Unified serializer for listing both outlines and scripts
    """
    uuid = serializers.UUIDField()
    title = serializers.CharField()
    type = serializers.CharField()  # 'outline' or 'script'
    status = serializers.CharField()
    status_display = serializers.CharField()
    word_count = serializers.IntegerField(allow_null=True)
    estimated_duration = serializers.FloatField(allow_null=True)
    created = serializers.DateTimeField()
    modified = serializers.DateTimeField()
    is_published = serializers.BooleanField(allow_null=True)
    version = serializers.IntegerField()


class StatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating status of outlines and scripts
    """
    status = serializers.ChoiceField(choices=[
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('saved', 'Saved'),
    ])