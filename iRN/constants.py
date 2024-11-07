def get_status_choices():
    """Get status choices for review requests."""
    DEFAULT_CHOICES = [
        ('pending', 'Pending'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('extended', 'Extended'),
        # ('forwarded', 'Forwarded'),
        # ('revised', 'Revised'),
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