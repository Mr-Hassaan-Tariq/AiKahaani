from django.contrib import admin
from .models import Niche, NicheTone, NichePacing


@admin.register(NicheTone)
class NicheToneAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(NichePacing)
class NichePacingAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Niche)
class NicheAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "admin",
        "status",
        "created",
        "modified",
    )
    list_filter = ("status", "admin")
    search_fields = ("title", "tagline")
    readonly_fields = ("created", "modified")
    ordering = ("-created",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("admin", "title", "prompt", "tagline", "thumbnail", "status"),
        }),
        ("Details", {
            "fields": (
                "script_structure",
                "tone",
                "pacing",
                "top_channels",
                "best_for",
            ),
        }),
        ("Timestamps", {
            "fields": ("created", "modified"),
        }),
    )
