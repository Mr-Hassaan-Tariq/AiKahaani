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
