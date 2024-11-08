from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def timesince_in_days(value):
    if not value:
        return 0
    
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    
    now = timezone.now()
    diff = now - value
    return diff.days 