from django import template
from ..models import MessageReadStatus

register = template.Library()

@register.filter
def get_read_status(message, user):
    """
    Check if a message has been read by the user.
    Usage: {{ message|get_read_status:request.user }}
    """
    try:
        # If we used prefetch_related with to_attr
        read_statuses = getattr(message, 'user_read_status', None)
        if read_statuses is not None:
            return read_statuses[0].is_read if read_statuses else False
    except (AttributeError, IndexError):
        pass
    
    # Fallback to database query if not prefetched
    return MessageReadStatus.objects.filter(
        message=message,
        user=user,
        is_read=True
    ).exists() 