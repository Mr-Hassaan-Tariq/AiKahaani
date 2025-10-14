# management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from scripts.models import Tone, TemplateStyle


class Command(BaseCommand):
    help = 'Seed the database with initial data for script generator'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Seeding database...')

            # Create Tones/Vibes
            tones_data = [
                'Informative',
                'Professional',
                'Entertaining',
                'Motivational',
                'Funny'
            ]

            for tone_name in tones_data:
                tone, created = Tone.objects.get_or_create(name=tone_name)
                if created:
                    self.stdout.write(f'Created tone: {tone_name}')

            # Create Template Styles (based on 140 WPM average English speaking rate)
            template_styles_data = [
                {
                    'name': 'Short',
                    'min_length': 2800,  # 20 min * 140 WPM
                    'max_length': 3000,  # ~21.4 min * 140 WPM
                    'duration': 20,  # 20 minutes
                    'description': 'Great for concise explainers or presentations'
                },
                {
                    'name': 'Medium',
                    'min_length': 5600,  # 40 min * 140 WPM
                    'max_length': 6000,  # ~42.9 min * 140 WPM
                    'duration': 40,  # 40 minutes
                    'description': 'Ideal for in-depth videos, product demos, interviews'
                },
                {
                    'name': 'Long',
                    'min_length': 8400,  # 60 min * 140 WPM
                    'max_length': 9000,  # ~64.3 min * 140 WPM
                    'duration': 60,  # 60 minutes
                    'description': 'Best for comprehensive tutorials, webinars, lectures'
                },
                {
                    'name': 'Flexible Outline',
                    'min_length': 100,
                    'max_length': 300,
                    'duration': 0,  # Flexible
                    'description': 'High-level structure without full script'
                }
            ]

            for style_data in template_styles_data:
                style, created = TemplateStyle.objects.get_or_create(
                    name=style_data['name'],
                    defaults={
                        'min_length': style_data['min_length'],
                        'max_length': style_data['max_length'],
                        'duration': style_data['duration'],
                        'description': style_data['description']
                    }
                )
                if created:
                    self.stdout.write(f'Created template style: {style_data["name"]}')
                else:
                    # Update if exists (to keep data in sync with UI spec)
                    for field, value in style_data.items():
                        setattr(style, field, value)
                    style.save()
                    self.stdout.write(f'Updated template style: {style_data["name"]}')

            self.stdout.write(
                self.style.SUCCESS('Successfully seeded database!')
            )
