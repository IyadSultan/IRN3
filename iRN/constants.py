from django.core.cache import cache
from django.apps import apps
from django.db import OperationalError

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


COINVESTIGATOR_ROLES = [
    ('PI', 'Principal Investigator'),
    ('CO_PI', 'Co-Principal Investigator'),
    ('SUB_I', 'Sub-Investigator'),
    ('DATA_MANAGER', 'Data Manager'),
    ('STATISTICIAN', 'Statistician'),
    ('CONSULTANT', 'Consultant'),
    ('OTHER', 'Other'),
]

SUBMISSION_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('rejected', 'Rejected'),
    ('accepted', 'Accepted'),
    ('revision_requested', 'Revision Requested'),
    ('closed', 'Closed'),
]

def get_submission_status_choices():
    """Get status choices for submissions."""
    DEFAULT_CHOICES = SUBMISSION_STATUS_CHOICES
    
    try:
        choices = cache.get('submission_status_choices')
        if not choices:
            StatusChoice = apps.get_model('submission', 'StatusChoice')
            choices = list(StatusChoice.objects.filter(is_active=True).values_list('code', 'label'))
            if choices:
                cache.set('submission_status_choices', choices)
        return choices or DEFAULT_CHOICES
    except (OperationalError, LookupError):
        return DEFAULT_CHOICES