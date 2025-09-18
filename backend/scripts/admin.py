from django.contrib import admin

from .models import (
    FullScript,
    Script,
    ScriptOutline,
    ScriptTitle,
    TemplateStyle,
    TitleTone,
    Tone,
)

# Register your models here.


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "title",
        "get_tones",
        "template_style",
        "is_published",
        "created",
    )
    list_filter = ("is_published", "tones", "template_style")
    search_fields = ("title", "description", "content")
    readonly_fields = ("uuid", "created", "modified")
    autocomplete_fields = ("template_style",)
    filter_horizontal = ("tones",)
    ordering = ("-created",)
    
    def get_tones(self, obj):
        return ", ".join([tone.name for tone in obj.tones.all()])
    get_tones.short_description = "Tones"


@admin.register(ScriptTitle)
class ScriptTitleAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "user",
        "script",
        "is_optimized_title",
        "titles_count",
        "created",
    )
    list_filter = ("is_optimized_title", "created")
    search_fields = ("user__email", "script__title", "prompt", "user_provided_title")
    list_per_page = 10
    list_max_show_all = 100
    list_display_links = ("uuid", "user", "script")
    list_select_related = ("user", "script")
    readonly_fields = ("uuid", "created", "modified")
    raw_id_fields = ("user", "script")
    autocomplete_fields = ("user", "script")
    ordering = ("-created",)


@admin.register(Tone)
class ToneAdmin(admin.ModelAdmin):
    list_display = ("name", "created")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TemplateStyle)
class TemplateStyleAdmin(admin.ModelAdmin):
    list_display = ("name", "min_length", "max_length", "duration", "created")
    list_filter = ("duration",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(ScriptOutline)
class ScriptOutlineAdmin(admin.ModelAdmin):
    list_display = ("uuid", "title", "script", "get_tones", "status", "version", "created")
    list_filter = ("status", "openai_model", "tones")
    search_fields = ("title", "outline_text")
    readonly_fields = ("uuid", "created", "modified", "tokens_used", "generation_time")
    raw_id_fields = ("script",)
    filter_horizontal = ("tones",)
    ordering = ("-created",)
    
    def get_tones(self, obj):
        return ", ".join([tone.name for tone in obj.tones.all()])
    get_tones.short_description = "Tones"


@admin.register(FullScript)
class FullScriptAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "title",
        "outline",
        "status",
        "word_count",
        "is_published",
        "created",
    )
    list_filter = ("status", "is_published", "openai_model")
    search_fields = ("title", "content")
    readonly_fields = (
        "uuid",
        "created",
        "modified",
        "word_count",
        "estimated_duration",
        "tokens_used",
        "generation_time",
    )
    raw_id_fields = ("outline",)
    ordering = ("-created",)


@admin.register(TitleTone)
class TitleToneAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("created", "modified")
