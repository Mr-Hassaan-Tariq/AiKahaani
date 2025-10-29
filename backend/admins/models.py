# Create your models here.

from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel

from .choices import NicheStatus

User = get_user_model()


class NicheTone(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class NichePacing(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Niche(TimeStampedModel):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=280)
    prompt = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to="niches/thumbnails/", blank=True, null=True)

    # JSON payloads
    script_structure = models.JSONField(blank=True, null=True)
    tone = models.JSONField(default=list, blank=True)  # List of tone names
    pacing = models.JSONField(default=list, blank=True)  # List of pacing names
    top_channels = models.JSONField(
        default=list, blank=True
    )  # e.g. [{"name": "Channel Name", "link": "https://youtube.com/..."}]
    best_for = models.JSONField(
        default=list, blank=True
    )  # e.g. ["Education","Crime & Mystery"]

    status = models.CharField(
        max_length=8, choices=NicheStatus.choices, default=NicheStatus.ACTIVE
    )

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["title"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(title=""), name="niche_title_non_empty"
            ),
            models.CheckConstraint(
                check=~models.Q(tagline=""), name="niche_tagline_non_empty"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"
