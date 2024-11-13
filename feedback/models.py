# Create a new file: feedback/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    screenshot = models.ImageField(upload_to='feedback_screenshots/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True, null=True)
    response_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.subject}"