# messaging/tests/test_models.py

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from messaging.models import Message, MessageReadStatus, MessageAttachment
from django.db.models.signals import m2m_changed
from messaging.signals import create_message_read_status

User = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture
def test_users():
    """Create test users for messaging tests"""
    sender = User.objects.create_user(
        username='sender',
        email='sender@test.com',
        password='testpass123',
        first_name='John',
        last_name='Sender'
    )
    recipient = User.objects.create_user(
        username='recipient',
        email='recipient@test.com',
        password='testpass123',
        first_name='Jane',
        last_name='Recipient'
    )
    return {'sender': sender, 'recipient': recipient}

@pytest.fixture
def test_message(test_users):
    """Create a test message"""
    message = Message.objects.create(
        sender=test_users['sender'],
        subject='Test Message',
        body='This is a test message body',
        study_name='Test Study'
    )
    message.recipients.add(test_users['recipient'])
    return message

class TestMessageModel:
    def test_message_creation(self, test_users):
        """Test basic message creation"""
        message = Message.objects.create(
            sender=test_users['sender'],
            subject='Test Subject',
            body='Test Body',
        )
        message.recipients.add(test_users['recipient'])
        
        assert message.subject == 'Test Subject'
        assert message.body == 'Test Body'
        assert message.sender == test_users['sender']
        assert message.recipients.count() == 1
        assert message.recipients.first() == test_users['recipient']

    def test_message_read_status(self, test_message, test_users):
        """Test read status creation"""
        read_status = MessageReadStatus.objects.get(
            user=test_users['recipient'],
            message=test_message
        )
        assert read_status is not None
        assert read_status.is_read == False

    def test_message_read_status_automatic_creation(self, test_users):
        """Test that read status is automatically created when recipients are added"""
        message = Message.objects.create(
            sender=test_users['sender'],
            subject='Test Subject',
            body='Test Body',
        )
        
        # Add recipient - this should trigger the signal
        message.recipients.add(test_users['recipient'])
        
        # Check if read status was created
        read_status = MessageReadStatus.objects.filter(
            user=test_users['recipient'],
            message=message
        ).first()
        
        assert read_status is not None
        assert read_status.is_read == False

    def test_message_archive(self, test_message):
        """Test message archiving"""
        test_message.delete()  # This should archive instead of delete
        archived_message = Message.objects.get(id=test_message.id)
        assert archived_message.is_archived == True

    def test_get_recipients_display(self, test_message, test_users):
        """Test the recipients display method"""
        assert test_users['recipient'].get_full_name() in test_message.get_all_recipients_display()

class TestMessageAttachments:
    @pytest.fixture
    def test_attachment(self, test_message):
        """Create a test attachment"""
        file_content = b'Test file content'
        test_file = SimpleUploadedFile("test.txt", file_content)
        return MessageAttachment.objects.create(
            message=test_message,
            file=test_file,
            filename='test.txt'
        )

    def test_attachment_creation(self, test_attachment):
        """Test creating message attachments"""
        assert test_attachment.filename == 'test.txt'
        assert test_attachment.message is not None

    def test_attachment_with_message(self, test_message):
        """Test sending a message with attachment"""
        file_content = b'Test file content'
        test_file = SimpleUploadedFile("test.txt", file_content)
        
        attachment = MessageAttachment.objects.create(
            message=test_message,
            file=test_file,
            filename='test.txt'
        )
        
        assert attachment in test_message.attachments.all()