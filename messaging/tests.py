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
