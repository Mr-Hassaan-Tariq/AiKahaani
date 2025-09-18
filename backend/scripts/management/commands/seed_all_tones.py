from django.core.management.base import BaseCommand

from scripts.models import TitleTone


class Command(BaseCommand):
    help = "Comprehensive seeder for all tone-related data including TitleTone model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing tones before seeding (WARNING: This will delete all existing tones)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating anything",
        )

    def handle(self, *args, **options):
        """
        Comprehensive seeder for TitleTone model with additional options
        """

        # Extended list of tones with descriptions
        tone_data = [
            {
                "name": "Controversial",
                "description": "Provocative tones that spark debate and discussion",
            },
            {
                "name": "Shocking",
                "description": "Extreme statements designed to grab immediate attention",
            },
            {
                "name": "Persuasive",
                "description": "Convincing language that encourages action or belief",
            },
            {
                "name": "Mysterious",
                "description": "Intriguing content that builds curiosity and suspense",
            },
            {
                "name": "Dramatic",
                "description": "Emotionally intense language that amplifies impact",
            },
            {
                "name": "Question-based",
                "description": "Titles formulated as questions to engage curiosity",
            },
            {
                "name": "Sarcastic",
                "description": "Ironic or mocking tone for humorous effect",
            },
            {
                "name": "Witty",
                "description": "Clever and amusing language that entertains",
            },
            {
                "name": "Neutral",
                "description": "Objective and balanced tone without emotional bias",
            },
            # Additional tones that might be useful
            {
                "name": "Educational",
                "description": "Informative tone focused on teaching and learning",
            },
            {
                "name": "Inspirational",
                "description": "Motivating language that uplifts and encourages",
            },
            {
                "name": "Urgent",
                "description": "Time-sensitive language that creates immediate action",
            },
        ]

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        if options["clear"] and not options["dry_run"]:
            self.stdout.write(
                self.style.WARNING("Clearing existing TitleTone records...")
            )
            deleted_count = TitleTone.objects.count()
            TitleTone.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_count} existing tone records")
            )

        created_count = 0
        existing_count = 0

        self.stdout.write(
            self.style.SUCCESS("Starting comprehensive TitleTone seeding...")
        )

        for tone_info in tone_data:
            tone_name = tone_info["name"]

            if options["dry_run"]:
                exists = TitleTone.objects.filter(name=tone_name).exists()
                if exists:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[DRY RUN] Would skip existing: {tone_name}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"[DRY RUN] Would create: {tone_name}")
                    )
                continue

            tone, created = TitleTone.objects.get_or_create(
                name=tone_name, defaults={"name": tone_name}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {tone_name}"))
                self.stdout.write(f'  Description: {tone_info["description"]}')
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(f"• Already exists: {tone_name}"))

        if not options["dry_run"]:
            # Summary
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("Comprehensive seeding completed!"))
            self.stdout.write(f"• Created: {created_count} new tones")
            self.stdout.write(f"• Existing: {existing_count} tones")
            self.stdout.write(f"• Total tones in database: {TitleTone.objects.count()}")

            self.stdout.write("\n" + self.style.SUCCESS("Usage Instructions:"))
            self.stdout.write(
                "• Manage tones via Django Admin: /admin/scripts/titletone/"
            )
            self.stdout.write("• API will now validate against these database values")
            self.stdout.write("• Add more tones through admin or extend this seeder")
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nDry run completed. Use without --dry-run to apply changes."
                )
            )
