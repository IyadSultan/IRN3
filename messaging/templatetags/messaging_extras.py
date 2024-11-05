from django import template
from messaging.models import MessageReadStatus

register = template.Library()

@register.filter
def get_read_status(message, user):
    try:
        status = MessageReadStatus.objects.get(message=message, user=user)
        return status.is_read
    except MessageReadStatus.DoesNotExist:
        return False