from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a new JWT token for a user by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email address')
        parser.add_argument(
            '--output-format',
            choices=['json', 'text'],
            default='text',
            help='Output format for the tokens (default: text)'
        )

    def handle(self, *args, **options):
        email = options['email']
        output_format = options['output_format']
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f"Found user: {user.email}")
            
            # Create a new token
            refresh = RefreshToken.for_user(user)
            
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            if output_format == 'json':
                import json
                token_data = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_email': user.email,
                    'user_id': user.id
                }
                self.stdout.write(json.dumps(token_data, indent=2))
            else:
                self.stdout.write(
                    self.style.SUCCESS('New token created successfully!')
                )
                self.stdout.write(f"Access Token: {access_token}")
                self.stdout.write(f"Refresh Token: {refresh_token}")
                self.stdout.write(f"User ID: {user.id}")
                self.stdout.write(f"User Email: {user.email}")
            
        except User.DoesNotExist:
            raise CommandError(f"User with email '{email}' not found")
        except Exception as e:
            raise CommandError(f"Error creating token: {str(e)}")
