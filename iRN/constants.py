from django.core.cache import cache
from django.apps import apps

def get_status_choices():
    """Get status choices for review requests."""
    DEFAULT_CHOICES = [
        ('pending', 'Pending'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('extended', 'Extended'),
        ('request_withdrawn', 'Request Withdrawn'),
    ]
    
    try:
        choices = cache.get('review_status_choices')
        if not choices:
            StatusChoice = apps.get_model('review', 'StatusChoice')
            choices = list(StatusChoice.objects.filter(is_active=True).values_list('code', 'label'))
            if choices:
                cache.set('review_status_choices', choices)
        return choices or DEFAULT_CHOICES
    except Exception:
        return DEFAULT_CHOICES

# User role choices
USER_ROLE_CHOICES = [
    ('KHCC investigator', 'KHCC investigator'),
    ('Non-KHCC investigator', 'Non-KHCC investigator'),
    ('Research Assistant/Coordinator', 'Research Assistant/Coordinator'),
    ('OSAR head', 'OSAR head'),
    ('OSAR', 'OSAR'),
    ('IRB chair', 'IRB chair'),
    ('RC coordinator', 'RC coordinator'),
    ('IRB member', 'IRB member'),
    ('RC chair', 'RC chair'),
    ('RC member', 'RC member'),
    ('AHARPP Head', 'AHARPP Head'),
    ('System administrator', 'System administrator'),
    ('CEO', 'CEO'),
    ('CMO', 'CMO'),
    ('AIDI Head', 'AIDI Head'),
    ('Grant Management Officer', 'Grant Management Officer'),
]