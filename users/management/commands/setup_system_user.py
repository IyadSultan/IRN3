from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates or updates the system user and its profile'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get or create system user
                system_user, user_created = User.objects.get_or_create(
                    username='system',
                    defaults={
                        'first_name': 'System',
                        'last_name': 'User',
                        'email': 'system@irn.com',
                        'is_active': False
                    }
                )

                # Get or create user profile
                profile, profile_created = UserProfile.objects.get_or_create(
                    user=system_user,
                    defaults={
                        'role': 'system'
                    }
                )

                if user_created:
                    self.stdout.write(self.style.SUCCESS('Successfully created system user'))
                else:
                    self.stdout.write(self.style.SUCCESS('System user already exists'))

                if profile_created:
                    self.stdout.write(self.style.SUCCESS('Successfully created system user profile'))
                else:
                    self.stdout.write(self.style.SUCCESS('System user profile already exists'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 