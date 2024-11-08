from django.contrib.auth import get_user_model
from django.db import transaction
from .settings import get_system_email, get_system_name, get_system_username

User = get_user_model()

def get_system_user():
    """Get or create the system user for automated messages"""
    with transaction.atomic():
        system_email = get_system_email()
        system_username = get_system_username()
        system_name = get_system_name()
        first_name, last_name = system_name.split(' ', 1) if ' ' in system_name else (system_name, '')
        
        # Try to get existing system user
        try:
            system_user = User.objects.select_related('userprofile').get(username=system_username)
            # Update email if it changed in settings
            if system_user.email != system_email:
                system_user.email = system_email
                system_user.first_name = first_name
                system_user.last_name = last_name
                system_user.save()
        except User.DoesNotExist:
            # Create new system user if it doesn't exist
            system_user = User.objects.create(
                username=system_username,
                email=system_email,
                is_active=False,
                first_name=first_name,
                last_name=last_name
            )

        return system_user