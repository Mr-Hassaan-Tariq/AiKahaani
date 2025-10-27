from django.db import transaction
from .models import UserTitles


from django.db import transaction

def save_generated_titles(user, titles, prompt=None, tones=None, user_title=None, script=None):
    """
    Save each generated title batch as a separate UserTitles entry.

    Args:
        user: The authenticated User instance.
        titles: List of generated titles.
        prompt: Prompt used for generation (optional).
        tones: List of tones applied (optional).
        user_title: Original user-provided title (optional).
        script: Related Script instance (optional).
    """
    if not user or not isinstance(titles, list):
        return

    # Clean titles: remove blanks and duplicates within the batch
    cleaned_titles = [t.strip() for t in titles if isinstance(t, str) and t.strip()]
    cleaned_titles = list(dict.fromkeys(cleaned_titles))  # preserve order, remove duplicates
    if not cleaned_titles:
        return

    with transaction.atomic():
        UserTitles.objects.create(
            user=user,
            titles=cleaned_titles,
            prompt=prompt,
            tones=tones or [],
            user_title=user_title,
            script=script,
        )

