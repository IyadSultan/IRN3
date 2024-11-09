# messaging/tests/test_models.py

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from messaging.models import Message, MessageReadStatus, MessageAttachment
from submission.models import Submission

User = get_user_model()

pytestmark = pytest.mark.django_db

class TestMessageModel:
    @pytest.fixture
    def setup_users(self):
        # Create users with proper full names
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='password',
            first_name='Test',
            last_name='Sender'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='password',
            first_name='Test',
            last_name='Recipient'
        )
        
        # Create a test submission
        self.submission = Submission.objects.create(
            title="Test Study",
            primary_investigator=self.sender,
            status='draft'
        )

    def test_message_read_status(self, setup_users):
        message = Message.objects.create(
            sender=self.sender,
            subject="Test Message",
            body="Test Body",
            related_submission=self.submission
        )
        message.recipients.add(self.recipient)
        
        # Test read status
        read_status = MessageReadStatus.objects.get(
            user=self.recipient,
            message=message
        )
        assert read_status is not None
        assert read_status.is_read == False

    def test_message_archive(self, setup_users):
        message = Message.objects.create(
            sender=self.sender,
            subject="Test Message",
            body="Test Body",
            related_submission=self.submission
        )
        message.recipients.add(self.recipient)
        
        # Test archiving
        message.delete()  # This should archive instead of delete
        archived_message = Message.objects.get(id=message.id)
        assert archived_message.is_archived == True

    def test_get_recipients_display(self, setup_users):
        message = Message.objects.create(
            sender=self.sender,
            subject="Test Message",
            body="Test Body",
            related_submission=self.submission
        )
        message.recipients.add(self.recipient)
        
        # Test recipients display
        assert "Test Recipient" in message.get_all_recipients_display()


class TestMessageAttachments:
    @pytest.fixture
    def setup_message(self):
        # Create users with proper full names
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='password',
            first_name='Test',
            last_name='Sender'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='password',
            first_name='Test',
            last_name='Recipient'
        )
        
        # Create a test submission
        self.submission = Submission.objects.create(
            title="Test Study",
            primary_investigator=self.sender,
            status='draft'
        )
        
        self.message = Message.objects.create(
            sender=self.sender,
            subject="Test Message",
            body="Test Body",
            related_submission=self.submission
        )
        self.message.recipients.add(self.recipient)
        return self.message

    def test_attachment_creation(self, setup_message):
        file_content = b'Test file content'
        test_file = SimpleUploadedFile("test.txt", file_content)
        
        attachment = MessageAttachment.objects.create(
            message=setup_message,
            file=test_file,
            filename='test.txt'
        )
        assert attachment.message == setup_message
        assert attachment.filename == 'test.txt'

    def test_attachment_with_message(self, setup_message):
        file_content = b'Test file content'
        test_file = SimpleUploadedFile("test.txt", file_content)
        
        attachment = MessageAttachment.objects.create(
            message=setup_message,
            file=test_file,
            filename='test.txt'
        )
        
        # Test relationship
        assert setup_message.attachments.count() == 1
        assert setup_message.attachments.first() == attachment