from django.conf import settings

def get_system_email():
    """Get system email from settings with fallback"""
    return getattr(settings, 'SYSTEM_EMAIL', 'system@irn.org')

def get_system_name():
    """Get system name from settings with fallback"""
    return getattr(settings, 'SYSTEM_NAME', 'AIDI System')

def get_system_username():
    """Get system username from settings with fallback"""
    return getattr(settings, 'SYSTEM_USERNAME', 'system') 