from django.apps import AppConfig
from django.template.library import Library

class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    def ready(self):
        # Remove the line that tries to get_template('dummy.html')
        # Instead, we'll just ensure the messaging_extras library is loaded
        try:
            Library.get_library('messaging_extras')
        except Exception as e:
            print(f"Error loading messaging_extras: {e}")
