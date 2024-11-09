from django.core.checks import Warning, register
from django.conf import settings

@register()
def check_email_configuration(app_configs, **kwargs):
    """
    Check if email settings are properly configured
    """
    errors = []

    # Check if email backend is configured
    if not hasattr(settings, 'EMAIL_BACKEND'):
        errors.append(
            Warning(
                'EMAIL_BACKEND is not configured.',
                hint='Set EMAIL_BACKEND in your settings file.',
                id='messaging.W001',
            )
        )

    # Check if email host is configured
    if not getattr(settings, 'EMAIL_HOST', None):
        errors.append(
            Warning(
                'EMAIL_HOST is not configured.',
                hint='Set EMAIL_HOST in your settings file.',
                id='messaging.W002',
            )
        )

    # Check if email credentials are configured for non-console backends
    if getattr(settings, 'EMAIL_BACKEND', '') != 'django.core.mail.backends.console.EmailBackend':
        if not getattr(settings, 'EMAIL_HOST_USER', None):
            errors.append(
                Warning(
                    'EMAIL_HOST_USER is not configured.',
                    hint='Set EMAIL_HOST_USER in your settings file.',
                    id='messaging.W003',
                )
            )
        if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
            errors.append(
                Warning(
                    'EMAIL_HOST_PASSWORD is not configured.',
                    hint='Set EMAIL_HOST_PASSWORD in your settings file.',
                    id='messaging.W004',
                )
            )

    return errors
