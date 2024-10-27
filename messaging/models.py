# messaging/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .validators import validate_file_size

from django.conf import settings

User = get_user_model()

# messaging/models.py

class MessageManager(models.Manager):
    def delete(self):
        # Prevent deletion, raise an exception
        raise Exception("Messages cannot be deleted. Use archive instead.")

def get_default_respond_by():
    return timezone.now() + timezone.timedelta(weeks=2)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipients = models.ManyToManyField(User, related_name='received_messages')
    cc = models.ManyToManyField(User, related_name='cc_messages', blank=True)
    bcc = models.ManyToManyField(User, related_name='bcc_messages', blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    study_name = models.CharField(max_length=255, blank=True, null=True)
    respond_by = models.DateTimeField(default=get_default_respond_by, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    attachments = models.FileField(upload_to='attachments/', validators=[validate_file_size], blank=True, null=True)
    hashtags = models.CharField(max_length=255, blank=True, null=True)
    
    objects = MessageManager()

    def delete(self, *args, **kwargs):
        # Override delete method to archive instead
        self.is_archived = True
        self.save()

    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return self.subject

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
