from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, MessageReadStatus

@receiver(post_save, sender='messaging.Message')
def create_message_read_status(sender, instance, created, **kwargs):
    if created:
        from .models import MessageReadStatus
        for recipient in instance.recipients.all():
            MessageReadStatus.objects.create(user=recipient, message=instance)

