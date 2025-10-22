from django.contrib import admin

from .models import (
    FullScript,
    OpenAIRunLog,
    Script,
    ScriptOutline,
    ScriptTitle,
    TemplateStyle,
    TitleTone,
    Tone,
    UserTitles
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
    list_display = (
        "uuid",
        "title",
        "user",
        "get_tones",
        "status",
        "version",
        "created",
    )
    list_filter = ("status", "openai_model", "tones")
    search_fields = ("title", "outline_text")
    readonly_fields = ("uuid", "created", "modified", "tokens_used", "generation_time")
    raw_id_fields = ("user",)
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


@admin.register(OpenAIRunLog)
class OpenAIRunLogAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "run_type",
        "user",
        "tokens_used",
        "word_count",
        "file_search_used",
        "status",
        "generation_time",
        "created",
    )
    list_filter = ("run_type", "status", "file_search_used", "created")
    search_fields = ("thread_id", "run_id", "assistant_id", "user__email")
    readonly_fields = (
        "uuid",
        "created",
        "modified",
        "thread_id",
        "run_id",
        "assistant_id",
        "tokens_used",
        "word_count",
        "file_search_used",
        "file_search_snippets",
        "run_type",
        "generation_time",
        "model",
        "status",
    )
    raw_id_fields = ("user", "script_outline", "full_script", "script_title")
    list_per_page = 20
    ordering = ("-created",)

    fieldsets = (
        ("Run Information", {"fields": ("uuid", "run_type", "status", "user")}),
        (
            "OpenAI Identifiers",
            {"fields": ("thread_id", "run_id", "assistant_id", "model")},
        ),
        ("Metrics", {"fields": ("tokens_used", "word_count", "generation_time")}),
        ("File Search", {"fields": ("file_search_used", "file_search_snippets")}),
        (
            "References",
            {
                "fields": ("script_outline", "full_script", "script_title"),
                "classes": ("collapse",),
            },
        ),
        ("Timestamps", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )


@admin.register(UserTitles)
class UserTitlesAdmin(admin.ModelAdmin):
    list_display = ("user", "created", "modified")
    search_fields = ("user__username",)
    list_filter = ("created",)
    readonly_fields = ("created", "modified")