# review/templatetags/review_tags.py

from django import template
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def get_user_name(user_id):
    """Get user's full name from ID."""
    try:
        user = User.objects.select_related('userprofile').get(id=user_id)
        return user.userprofile.full_name
    except User.DoesNotExist:
        return f"Unknown User ({user_id})"

@register.simple_tag
def get_reviewer_role(user):
    """Get primary role of a reviewer."""
    role_hierarchy = [
        'OSAR',
        'IRB Head',
        'Research Council Head',
        'AHARPP Head',
        'IRB Member',
        'Research Council Member',
        'AHARPP Reviewer'
    ]
    
    for role in role_hierarchy:
        if user.groups.filter(name=role).exists():
            return role
    return 'Unknown Role'

@register.filter
def timesince_in_days(value):
    if not value:
        return 0
    
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    
    now = timezone.now()
    diff = now - value
    return diff.days