from django.core.management.base import BaseCommand

from scripts.models import TitleTone


class Command(BaseCommand):
    help = "Seed TitleTone model with predefined tone values"

    def handle(self, *args, **options):
        """
        Seed the TitleTone model with predefined values based on the
        tone validation logic in the serializer
        """

        # Predefined tones based on the validation logic
        predefined_tones = [
            "Controversial",
            "Shocking",
            "Persuasive",
            "Mysterious",
            "Dramatic",
            "Question-based",
            "Sarcastic",
            "Witty",
            "Neutral",
        ]

        created_count = 0
        existing_count = 0

        self.stdout.write(self.style.SUCCESS("Starting TitleTone seeding process..."))

        for tone_name in predefined_tones:
            tone, created = TitleTone.objects.get_or_create(
                name=tone_name, defaults={"name": tone_name}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created tone: {tone_name}"))
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"• Tone already exists: {tone_name}")
                )

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))
        self.stdout.write(f"• Created: {created_count} new tones")
        self.stdout.write(f"• Existing: {existing_count} tones")
        self.stdout.write(f"• Total tones in database: {TitleTone.objects.count()}")

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "\nYou can now manage tones through Django Admin or add more via this command."
                )
            )
