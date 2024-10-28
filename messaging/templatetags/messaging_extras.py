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

# Define your custom template tags and filters here
@register.filter
def example_filter(value):
    return value

@register.simple_tag
def example_tag():
    return "This is an example tag"

