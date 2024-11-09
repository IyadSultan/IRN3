# messaging/signals.py

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Message, MessageReadStatus

@receiver(m2m_changed, sender=Message.recipients.through)
def create_message_read_status(sender, instance, action, pk_set, **kwargs):
    """Create read status for all recipients when they are added to a message"""
    if action == "post_add" and pk_set:
        for user_id in pk_set:
            MessageReadStatus.objects.get_or_create(
                message=instance,
                user_id=user_id,
                defaults={'is_read': False}
            )