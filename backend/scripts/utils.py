from django.db import transaction
from .models import UserTitles


def save_generated_titles(user, new_titles):
    """
    Save generated titles for a user.
    - Creates a new UserTitles record if none exists.
    - Appends only new, non-empty, unique titles.
    """
    if not user or not isinstance(new_titles, list):
        return

    # Clean titles: strip whitespace and remove empty strings
    cleaned_titles = [t.strip() for t in new_titles if isinstance(t, str) and t.strip()]
    if not cleaned_titles:
        return

    with transaction.atomic():
        user_titles, _ = UserTitles.objects.get_or_create(user=user)
        existing_titles = user_titles.titles or []

        # Add only unique titles not already saved
        combined_titles = existing_titles + [
            t for t in cleaned_titles if t not in existing_titles
        ]

        if combined_titles != existing_titles:
            user_titles.titles = combined_titles
            user_titles.save(update_fields=["titles", "modified"])
