# tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_review_reminders():
    upcoming_deadlines = ReviewRequest.objects.filter(
        status='pending',
        deadline__lte=timezone.now() + timedelta(days=2)
    )
    for request in upcoming_deadlines:
        send_reminder_email(request)