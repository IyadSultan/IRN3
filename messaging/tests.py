# messaging/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user,
            subject='Test Message',
            body='This is a test message.'
        )
        self.assertEqual(message.subject, 'Test Message')

from django.core.mail import send_mail
from django.conf import settings

def test_email_configuration():
    try:
        send_mail(
            subject='Test Email Configuration',
            message='This is a test email to verify the email configuration.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        return True, "Test email sent successfully"
    except Exception as e:
        return False, f"Error sending test email: {str(e)}"
