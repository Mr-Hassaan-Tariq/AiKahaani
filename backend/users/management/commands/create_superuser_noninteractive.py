import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser non-interactively using environment variables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            help="Email address for the superuser (or use DJANGO_SUPERUSER_EMAIL env var)",
        )
        parser.add_argument(
            "--username",
            type=str,
            help="Username for the superuser (or use DJANGO_SUPERUSER_USERNAME env var)",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password for the superuser (or use DJANGO_SUPERUSER_PASSWORD env var)",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Do not prompt for input",
        )

    def handle(self, *args, **options):
        # Get values from arguments or environment variables
        email = options.get("email") or os.environ.get("DJANGO_SUPERUSER_EMAIL")
        username = options.get("username") or os.environ.get(
            "DJANGO_SUPERUSER_USERNAME"
        )
        password = options.get("password") or os.environ.get(
            "DJANGO_SUPERUSER_PASSWORD"
        )

        # Validate required fields
        if not email:
            raise CommandError(
                "Email is required. Provide --email or set DJANGO_SUPERUSER_EMAIL environment variable."
            )

        if not username:
            raise CommandError(
                "Username is required. Provide --username or set DJANGO_SUPERUSER_USERNAME environment variable."
            )

        if not password:
            raise CommandError(
                "Password is required. Provide --password or set DJANGO_SUPERUSER_PASSWORD environment variable."
            )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email "{email}" already exists.')
            )
            user = User.objects.get(email=email)
            # Update to superuser if not already
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'User "{email}" updated to superuser.')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'User "{email}" is already a superuser.')
                )
            return

        # Create the superuser
        try:
            user = User.objects.create_superuser(
                email=email,
                username=username,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{email}" created successfully!')
            )
            self.stdout.write(f"  Email: {user.email}")
            self.stdout.write(f"  Username: {user.username}")
            self.stdout.write(f"  Is Superuser: {user.is_superuser}")
            self.stdout.write(f"  Is Staff: {user.is_staff}")
        except Exception as e:
            raise CommandError(f"Error creating superuser: {str(e)}") from e
