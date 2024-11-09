from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile for new users if it doesn't exist"""
    if instance.username == 'system':
        return
        
    # Only create if it doesn't exist
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            'full_name': f"{instance.first_name} {instance.last_name}".strip() or instance.username
        }
    )