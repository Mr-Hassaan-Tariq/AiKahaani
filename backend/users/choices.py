from django.db import models
from django.utils.translation import gettext_lazy as _


class LanguageChoices(models.TextChoices):
    ENGLISH = "en", _("English")
    SPANISH = "es", _("Spanish")
    FRENCH = "fr", _("French")
    GERMAN = "de", _("German")
    ITALIAN = "it", _("Italian")
    PORTUGUESE = "pt", _("Portuguese")
    RUSSIAN = "ru", _("Russian")
    JAPANESE = "ja", _("Japanese")
    CHINESE = "zh", _("Chinese")
    ARABIC = "ar", _("Arabic")


class UserRoles(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
