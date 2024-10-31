from django.contrib.auth.models import User
from django.db import transaction
from .models import SystemSettings

def get_system_user():
    """Get or create the system user for automated messages"""
    with transaction.atomic():
        system_email = SystemSettings.get_system_email()
        
        # Try to get existing system user
        try:
            system_user = User.objects.select_related('userprofile').get(username='system')
            # Update email if it changed in settings
            if system_user.email != system_email:
                system_user.email = system_email
                system_user.save()
        except User.DoesNotExist:
            # Create new system user if it doesn't exist
            system_user = User.objects.create(
                username='system',
                email=system_email,
                is_active=False,
                first_name='AIDI',
                last_name='System'
            )

        return system_user