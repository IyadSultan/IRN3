# messaging/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .validators import validate_file_size, validate_file_extension  # Import validators

import uuid

User = get_user_model()

class MessageManager(models.Manager):
    def delete(self):
        # Prevent deletion, raise an exception
        raise Exception("Messages cannot be deleted. Use archive instead.")

def get_default_respond_by():
    return timezone.now() + timezone.timedelta(weeks=2)

class MessageAttachment(models.Model):
    message = models.ForeignKey('Message', related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='message_attachments/',
        validators=[validate_file_size, validate_file_extension]  # Apply validators
    )
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg']

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = self.file.name.split('/')[-1]
        super().save(*args, **kwargs)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipients = models.ManyToManyField(User, related_name='received_messages')
    cc = models.ManyToManyField(User, related_name='cc_messages', blank=True)
    bcc = models.ManyToManyField(User, related_name='bcc_messages', blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    respond_by = models.DateTimeField(default=get_default_respond_by, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    hashtags = models.CharField(max_length=255, blank=True, null=True)
    thread_id = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    related_submission = models.ForeignKey(
        'submission.Submission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_messages'
    )
    objects = MessageManager()
    message_type = models.CharField(
    max_length=20,
        choices=[
            ('decision', 'Decision'),
            ('notification', 'Notification'),
            ('general', 'General'),
        ],
        default='general'
)

    def get_recipients_display(self):
        """Returns a formatted string of recipient names."""
        recipients = self.recipients.all()
        if not recipients:
            return "-"

        first_recipient = recipients.first()
        first_name = first_recipient.get_full_name() or first_recipient.username

        if recipients.count() > 1:
            return f"{first_name} +{recipients.count() - 1}"
        return first_name

    def get_all_recipients_display(self):
        """Returns a comma-separated list of all recipient names."""
        return ", ".join(
            recipient.get_full_name() or recipient.username
            for recipient in self.recipients.all()
        )

    def delete(self, *args, **kwargs):
        # Override delete method to archive instead
        self.is_archived = True
        self.save()

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return self.subject

class NotificationStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_key = models.CharField(max_length=255)
    dismissed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification_key')

class MessageReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='read_statuses', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message.subject} - {'Read' if self.is_read else 'Unread'}"

class Comment(models.Model):
    message = models.ForeignKey(Message, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.message.subject}"
