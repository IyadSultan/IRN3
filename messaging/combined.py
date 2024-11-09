from django.contrib import admin

# Register your models here.
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
from django.core.checks import Warning, register
from django.conf import settings

@register()
def check_email_configuration(app_configs, **kwargs):
    """
    Check if email settings are properly configured
    """
    errors = []

    # Check if email backend is configured
    if not hasattr(settings, 'EMAIL_BACKEND'):
        errors.append(
            Warning(
                'EMAIL_BACKEND is not configured.',
                hint='Set EMAIL_BACKEND in your settings file.',
                id='messaging.W001',
            )
        )

    # Check if email host is configured
    if not getattr(settings, 'EMAIL_HOST', None):
        errors.append(
            Warning(
                'EMAIL_HOST is not configured.',
                hint='Set EMAIL_HOST in your settings file.',
                id='messaging.W002',
            )
        )

    # Check if email credentials are configured for non-console backends
    if getattr(settings, 'EMAIL_BACKEND', '') != 'django.core.mail.backends.console.EmailBackend':
        if not getattr(settings, 'EMAIL_HOST_USER', None):
            errors.append(
                Warning(
                    'EMAIL_HOST_USER is not configured.',
                    hint='Set EMAIL_HOST_USER in your settings file.',
                    id='messaging.W003',
                )
            )
        if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
            errors.append(
                Warning(
                    'EMAIL_HOST_PASSWORD is not configured.',
                    hint='Set EMAIL_HOST_PASSWORD in your settings file.',
                    id='messaging.W004',
                )
            )

    return errors
import os

# delete combined.py
try:    
    os.remove('combined.py')
except FileNotFoundError:
    pass

app_directory = '../messaging/'
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/messaging/'


# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if not self.scope["user"].is_anonymous:
            await self.channel_layer.group_discard(
                f"user_{self.scope['user'].id}",
                self.channel_name
            )

    async def notify(self, event):
        """Send notification to WebSocket"""
        await self.send_json(event["data"])

    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        command = content.get("command", None)
        if command == "get_unread_count":
            count = await self.get_unread_count()
            await self.send_json({
                "type": "unread_count",
                "count": count
            })

    @database_sync_to_async
    def get_unread_count(self):
        """Get unread message count for current user"""
        cache_key = f'unread_count_{self.scope["user"].id}'
        count = cache.get(cache_key)
        if count is None:
            from .models import MessageReadStatus
            count = MessageReadStatus.objects.filter(
                user=self.scope["user"],
                is_read=False
            ).count()
            cache.set(cache_key, count, 300)  # Cache for 5 minutes
        return count
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from submission.models import Submission
from .models import Message, MessageAttachment

class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-user-field',
            'data-placeholder': 'Select recipients...'
        })
    )
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-user-field',
            'data-placeholder': 'Select CC recipients...'
        })
    )
    bcc = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-user-field',
            'data-placeholder': 'Select BCC recipients...'
        })
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    related_submission = forms.ModelChoiceField(
        queryset=Submission.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Link to a submission...'
        })
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'recipients', 'cc', 'bcc', 'related_submission']

    def clean(self):
        cleaned_data = super().clean()
        recipients = cleaned_data.get('recipients')
        
        if not recipients:
            self.add_error('recipients', 'At least one recipient is required.')
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Exclude current user from recipients
            excluded_user_queryset = User.objects.exclude(id=user.id).filter(is_active=True)
            self.fields['recipients'].queryset = excluded_user_queryset
            self.fields['cc'].queryset = excluded_user_queryset
            self.fields['bcc'].queryset = excluded_user_queryset
            
            # Update related_submission queryset
            if user.is_authenticated:
                accessible_submissions = Submission.objects.filter(
                    Q(primary_investigator=user) |
                    Q(coinvestigators__user=user) |  # Changed to access user through CoInvestigator
                    Q(research_assistants__user=user)
                ).distinct()
                self.fields['related_submission'].queryset = accessible_submissions

        for field in self.fields:
            if field not in ['recipients', 'cc', 'bcc', 'related_submission', 'attachment']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)# messaging/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .validators import validate_file_size

from django.conf import settings

import uuid

User = get_user_model()

# messaging/models.py

class MessageManager(models.Manager):
    def delete(self):
        # Prevent deletion, raise an exception
        raise Exception("Messages cannot be deleted. Use archive instead.")

def get_default_respond_by():
    return timezone.now() + timezone.timedelta(weeks=2)

class MessageAttachment(models.Model):
    message = models.ForeignKey('Message', related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='message_attachments/')
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
    study_name = models.CharField(max_length=255, blank=True, null=True)
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
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, MessageReadStatus

@receiver(post_save, sender='messaging.Message')
def create_message_read_status(sender, instance, created, **kwargs):
    if created:
        from .models import MessageReadStatus
        for recipient in instance.recipients.all():
            MessageReadStatus.objects.create(user=recipient, message=instance)

from celery import shared_task
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task(bind=True, max_retries=3)
def send_message_email_task(self, message_id):
    """Celery task to send email notifications"""
    try:
        message = Message.objects.select_related('sender').prefetch_related(
            'recipients', 'cc', 'bcc', 'attachments'
        ).get(id=message_id)
        
        recipients_emails = [user.email for user in message.recipients.all()]
        cc_emails = [user.email for user in message.cc.all()]
        bcc_emails = [user.email for user in message.bcc.all()]
        
        if not any([recipients_emails, cc_emails, bcc_emails]):
            return "No recipients to send email to."
        
        with get_connection() as connection:
            # Prepare email content
            html_content = render_to_string('messaging/email/message_notification.html', {
                'message': message,
                'sender': message.sender,
                'view_url': f"{settings.SITE_URL}/messaging/message/{message.id}/",
            })
            text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=message.subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=recipients_emails,
                cc=cc_emails,
                bcc=bcc_emails,
                connection=connection,
                reply_to=[message.sender.email]
            )
            
            # Attach HTML content
            email.attach_alternative(html_content, "text/html")
            
            # Attach files
            for attachment in message.attachments.all():
                email.attach(attachment.filename, attachment.file.read())
            
            # Send email
            email.send()
            
        return "Email sent successfully"
        
    except Exception as exc:
        # Retry the task in case of failure
        self.retry(exc=exc, countdown=60 * 5)  # Retry after 5 minutes

# Signal to send email after message is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """Handle new message creation and send email notifications"""
    if created:
        send_message_email_task.delay(instance.id)
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
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('compose/', views.compose_message, name='compose_message'),
    path('compose_request/', views.ComposeMessageView.as_view(), name='compose'),
    path('message/<int:message_id>/', views.view_message, name='view_message'),
    path('reply/<int:message_id>/', views.reply, name='reply'),
    path('reply-all/<int:message_id>/', views.reply_all, name='reply_all'),
    path('forward/<int:message_id>/', views.forward, name='forward'),
    path('search/', views.search_messages, name='search_messages'),
    path('archive/', views.archive_message, name='archive_message'),
    path('delete/', views.delete_messages, name='delete_messages'),
    path('archived/', views.archived_messages, name='archived_messages'),
    path('threads/', views.threads_inbox, name='threads_inbox'),
    path('user-autocomplete/', views.user_autocomplete, name='user_autocomplete'),
    path('submission-autocomplete/', views.submission_autocomplete, name='submission_autocomplete'),
    path('dismiss-notification/', views.dismiss_notification, name='dismiss_notification'),
    path('update-read-status/', views.update_read_status, name='update_read_status'),
    path('archive-message/', views.archive_message, name='archive_message'),
]
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from typing import List, Optional
from .models import Message

def send_message_email(message: Message) -> None:
    """Send email notification for a message to all recipients"""
    with get_connection() as connection:
        subject = message.subject
        from_email = settings.EMAIL_HOST_USER
        
        # Prepare HTML content
        html_content = render_to_string('messaging/email/message_notification.html', {
            'message': message,
            'sender': message.sender,
            'view_url': f"{settings.SITE_URL}/messaging/view/{message.id}/",
        })
        text_content = strip_tags(html_content)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[r.email for r in message.recipients.all()],
            cc=[r.email for r in message.cc.all()],
            bcc=[r.email for r in message.bcc.all()],
            connection=connection,
            reply_to=[message.sender.email]
        )
        
        # Attach HTML content
        email.attach_alternative(html_content, "text/html")
        
        # Attach files if any
        for attachment in message.attachments.all():
            email.attach_file(attachment.file.path)
        
        # Send email
        email.send()# messaging/validators.py

from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_kb = 10240  # 10 MB
    if value.size > max_kb * 1024:
        raise ValidationError('Maximum file size is 10 MB')
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Prefetch
from django.contrib import messages
from django.template.defaulttags import register
from .models import Message, MessageReadStatus, Comment, MessageAttachment, NotificationStatus
from .forms import MessageForm, SearchForm
from submission.models import Submission
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin


User = get_user_model()

@login_required
def inbox(request):

    messages_list = Message.objects.filter(
        recipients=request.user, 
        is_archived=False
    ).order_by('-sent_at')
    
    # Add read status to the queryset
    messages_list = messages_list.prefetch_related(
        Prefetch(
            'read_statuses',
            queryset=MessageReadStatus.objects.filter(user=request.user),
            to_attr='user_read_status'
        )
    )
    
    # Check if notification has been dismissed
    notification_key = 'submission_2_confirmation'  # Use a unique key for each notification
    notification_dismissed = NotificationStatus.objects.filter(
        user=request.user,
        notification_key=notification_key
    ).exists()
    
    context = {
        'messages': messages_list,
        'show_notification': not notification_dismissed
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def dismiss_notification(request):
    if request.method == 'POST':
        notification_key = request.POST.get('notification_key')
        NotificationStatus.objects.get_or_create(
            user=request.user,
            notification_key=notification_key
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

    
@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
    return render(request, 'messaging/sent_messages.html', {
        'messages': messages,
        'is_archived': False
    })

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    # Update read status when viewing the message
    read_status, created = MessageReadStatus.objects.get_or_create(
        user=request.user,
        message=message,
        defaults={'is_read': True}
    )
    
    if not read_status.is_read:
        read_status.is_read = True
        read_status.save()
    
    return render(request, 'messaging/view_message.html', {'message': message})

@register.filter
def get_read_status(message, user):
    """
    Check if a message has been read by the user.
    Usage: {{ message|get_read_status:request.user }}
    """
    try:
        # If we used prefetch_related with to_attr
        read_statuses = getattr(message, 'user_read_status', None)
        if read_statuses is not None:
            return read_statuses[0].is_read if read_statuses else False
    except (AttributeError, IndexError):
        pass
    
    # Fallback to database query if not prefetched
    return MessageReadStatus.objects.filter(
        message=message,
        user=user,
        is_read=True
    ).exists()

@login_required
def compose_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                
                # Save many-to-many relationships after saving the message
                form.save_m2m()
                
                print(f"Message created: {message.id}")  # Debug print
                
                # Check if read statuses were created
                read_statuses = MessageReadStatus.objects.filter(message=message)
                print(f"Read statuses created: {read_statuses.count()}")  # Debug print
                
                messages.success(request, 'Message sent successfully!')
                return redirect('messaging:inbox')
            except Exception as e:
                print(f"Error sending message: {str(e)}")  # Debug print
                messages.error(request, f'Error sending message: {str(e)}')
        else:
            print(f"Form errors: {form.errors}")  # Debug print
            messages.error(request, 'Please correct the form errors.')
    else:
        form = MessageForm(user=request.user)
    
    return render(request, 'messaging/compose_message.html', {
        'form': form
    })

@login_required
def reply(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.thread_id = original_message.thread_id  # Use the same thread ID
            new_message.save()
            new_message.recipients.add(original_message.sender)
            form.save_m2m()
            messages.success(request, 'Reply sent successfully.')
            return redirect('messaging:inbox')
    else:
        form = MessageForm(initial={
            'subject': f"Re: {original_message.subject}",
            'body': f"\n\nOn {original_message.sent_at}, {original_message.sender.get_full_name()} wrote:\n{original_message.body}",
            'study_name': original_message.study_name,
            'recipients': original_message.sender.username,
        })
    return render(request, 'messaging/compose_message.html', {'form': form, 'is_reply': True})

@login_required
def reply_all(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.thread_id = original_message.thread_id  # Use the same thread ID
            new_message.save()
            form.save_m2m()
            messages.success(request, 'Reply to all sent successfully.')
            return redirect('messaging:inbox')
    else:
        # Get all recipients excluding current user
        all_recipients = list(original_message.recipients.exclude(id=request.user.id).values_list('username', flat=True))
        # Add original sender to recipients list
        if original_message.sender != request.user:
            all_recipients.append(original_message.sender.username)
        recipients_str = ', '.join(all_recipients)

        form = MessageForm(initial={
            'subject': f"Re: {original_message.subject}",
            'body': f"\n\nOn {original_message.sent_at}, {original_message.sender.get_full_name()} wrote:\n{original_message.body}",
            'study_name': original_message.study_name,
            'recipients': recipients_str,
            'cc': ', '.join([user.username for user in original_message.cc.all()]),
        })
    return render(request, 'messaging/compose_message.html', {'form': form, 'is_reply_all': True})

@login_required
def forward(request, message_id):
    original_message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.thread_id = original_message.thread_id  # Use the same thread ID
            new_message.save()
            form.save_m2m()
            messages.success(request, 'Message forwarded successfully.')
            return redirect('messaging:inbox')
    else:
        form = MessageForm(initial={
            'subject': f"Fwd: {original_message.subject}",
            'body': f"\n\n---------- Forwarded message ----------\nFrom: {original_message.sender.get_full_name()}\nDate: {original_message.sent_at}\nSubject: {original_message.subject}\nTo: {', '.join([r.get_full_name() for r in original_message.recipients.all()])}\n\n{original_message.body}",
            'study_name': original_message.study_name,
        })
    return render(request, 'messaging/compose_message.html', {'form': form, 'is_forward': True})

@login_required
def search_messages(request):
    query = request.GET.get('q', '')
    messages_list = []

    if query:
        messages_list = Message.objects.filter(
            Q(recipients=request.user) | Q(sender=request.user),
            Q(subject__icontains=query) | 
            Q(body__icontains=query) |
            Q(study_name__icontains=query)
        ).distinct().order_by('-sent_at')

    context = {
        'messages': messages_list,
        'query': query,
    }
    return render(request, 'messaging/search_results.html', context)



@login_required
def archive_message(request):
    if request.method == 'POST':
        message_ids = request.POST.getlist('selected_messages[]')
        messages_to_archive = Message.objects.filter(
            id__in=message_ids,
            recipients=request.user
        )
        
        messages_to_archive.update(is_archived=True)
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_messages(request):
    if request.method == 'POST':
        message_ids = request.POST.getlist('selected_messages')
        Message.objects.filter(id__in=message_ids, sender=request.user).delete()
        messages.success(request, f"{len(message_ids)} messages deleted.")
    return redirect('messaging:sent_messages')

@login_required
def archived_messages(request):
    messages_list = Message.objects.filter(recipients=request.user, is_archived=True).order_by('-sent_at')
    return render(request, 'messaging/archived_messages.html', {'messages': messages_list})

@login_required
def threads_inbox(request):
    # Get all messages for the user
    user_messages = Message.objects.filter(recipients=request.user)

    # Group messages by thread_id and count them
    threads = user_messages.values('thread_id').annotate(thread_count=Count('id')).filter(thread_count__gt=1)

    # Get the first message of each thread
    first_messages = Message.objects.filter(thread_id__in=[thread['thread_id'] for thread in threads]).order_by('sent_at')

    context = {
        'first_messages': first_messages,
    }
    return render(request, 'messaging/threads_inbox.html', context)

@login_required
def user_autocomplete(request):
    """View for handling user autocomplete requests"""
    term = request.GET.get('term', '')
    users = User.objects.filter(
        Q(userprofile__full_name__icontains=term) |
        Q(email__icontains=term) |
        Q(username__icontains=term)
    ).distinct()[:10]

    results = []
    for user in users:
        full_name = user.userprofile.full_name if hasattr(user, 'userprofile') else f"{user.first_name} {user.last_name}"
        results.append({
            'id': user.id,
            'value': full_name,
            'label': f"{full_name} ({user.email})"
        })

    return JsonResponse(results, safe=False)


@login_required
def submission_autocomplete(request):
    """API endpoint for submission autocomplete"""
    term = request.GET.get('term', '')
    
    submissions = Submission.objects.filter(
        Q(title__icontains=term) |
        Q(irb_number__icontains=term)
    ).distinct()[:10]
    
    results = []
    for submission in submissions:
        results.append({
            'id': submission.temporary_id,  # Use temporary_id instead of id
            'title': submission.title,
            'irb_number': submission.irb_number,
            'text': f"{submission.title} (IRB: {submission.irb_number})" if submission.irb_number else submission.title
        })
    
    return JsonResponse(results, safe=False)  # Return array directly like user_autocomplete

class ComposeMessageView(LoginRequiredMixin, CreateView):
    template_name = 'messaging/compose_message.html'
    form_class = MessageForm
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Get URL parameters
        recipient_id = self.request.GET.get('recipient')
        submission_id = self.request.GET.get('submission')
        
        if recipient_id:
            try:
                recipient = User.objects.get(id=recipient_id)
                initial['recipients'] = [{
                    'id': recipient.id,
                    'text': recipient.get_full_name() or recipient.email
                }]
            except User.DoesNotExist:
                pass
                
        if submission_id:
            try:
                submission = Submission.objects.get(id=submission_id)
                initial['related_submission'] = submission
            except Submission.DoesNotExist:
                pass
                
        return initial

@login_required
def update_read_status(request):
    if request.method == 'POST':
        message_ids = request.POST.getlist('message_ids[]')
        is_read = request.POST.get('is_read') == 'true'
        
        for message_id in message_ids:
            read_status, created = MessageReadStatus.objects.get_or_create(
                user=request.user,
                message_id=message_id,
                defaults={'is_read': is_read}
            )
            if not created:
                read_status.is_read = is_read
                read_status.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Archived Messages{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Archived Messages</h1>
    
    <div class="table-responsive">
        <table id="archived-messages-table" class="table table-striped table-hover">
            <thead class="thead-light">
                <tr>
                    <th>From</th>
                    <th>Subject</th>
                    <th>Study Name</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {% for message in messages %}
                <tr>
                    <td>{{ message.sender.username }}</td>
                    <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                    <td>{{ message.study_name|default_if_none:"-" }}</td>
                    <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        $('#archived-messages-table').DataTable({
            "order": [[3, "desc"]]
        });
    });
</script>
{% endblock %}
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
<link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet" />
<link href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css" rel="stylesheet" />
<style>
    .message-sidebar {
        min-height: calc(100vh - 60px);
        border-right: 1px solid #dee2e6;
        padding: 1rem;
    }
    
    .message-list-item {
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
        transition: background-color 0.2s;
    }
    
    .message-list-item:hover {
        background-color: #f8f9fa;
    }
    
    .message-list-item.unread {
        background-color: #e7f5ff;
    }
    
    .message-sender {
        font-weight: 500;
    }
    
    .message-preview {
        color: #6c757d;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .attachment-badge {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        background-color: #e9ecef;
        border-radius: 1rem;
    }
    
    .select2-container--bootstrap-5 .select2-selection {
        border: 1px solid #dee2e6;
    }
    
    .message-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .btn-compose {
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .message-count-badge {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
    }
    
    @media (max-width: 768px) {
        .message-sidebar {
            min-height: auto;
            border-right: none;
            border-bottom: 1px solid #dee2e6;
            margin-bottom: 1rem;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar -->
        <div class="col-md-3 col-lg-2 message-sidebar">
            <a href="{% url 'messaging:compose_message' %}" class="btn btn-primary btn-compose">
                <i class="fas fa-pen"></i> Compose
            </a>
            
            <div class="nav flex-column nav-pills">
                <a href="{% url 'messaging:inbox' %}" class="nav-link {% if request.resolver_match.view_name == 'messaging:inbox' %}active{% endif %}">
                    <i class="fas fa-inbox"></i> Inbox
                    {% if unread_count %}
                    <span class="badge bg-danger float-end message-count-badge">{{ unread_count }}</span>
                    {% endif %}
                </a>
                <a href="{% url 'messaging:sent_messages' %}" class="nav-link {% if request.resolver_match.view_name == 'messaging:sent_messages' %}active{% endif %}">
                    <i class="fas fa-paper-plane"></i> Sent
                </a>
                <a href="{% url 'messaging:archived_messages' %}" class="nav-link {% if request.resolver_match.view_name == 'messaging:archived_messages' %}active{% endif %}">
                    <i class="fas fa-archive"></i> Archived
                </a>
                <a href="{% url 'messaging:threads_inbox' %}" class="nav-link {% if request.resolver_match.view_name == 'messaging:threads_inbox' %}active{% endif %}">
                    <i class="fas fa-comments"></i> Threads
                </a>
            </div>
            
            <hr>
            
            <!-- Search Form -->
            <form method="get" action="{% url 'messaging:search_messages' %}" class="mb-3">
                <div class="input-group">
                    <input type="text" name="q" class="form-control" placeholder="Search messages...">
                    <button type="submit" class="btn btn-outline-secondary">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </form>
        </div>
        
        <!-- Main Content -->
        <div class="col-md-9 col-lg-10 p-4">
            {% block messaging_content %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
<script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>

<script>
$(document).ready(function() {
    // Initialize Select2
    $('.select2').select2({
        theme: 'bootstrap-5',
        width: '100%'
    });
    
    // Initialize DataTables
    $('.datatable').DataTable({
        pageLength: 25,
        ordering: true,
        responsive: true,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search messages...",
            paginate: {
                previous: '<i class="fas fa-chevron-left"></i>',
                next: '<i class="fas fa-chevron-right"></i>'
            }
        }
    });
    
    // Select all checkbox functionality
    $('#select-all').on('click', function() {
        $('.message-checkbox').prop('checked', this.checked);
        updateBulkActions();
    });
    
    $('.message-checkbox').on('change', function() {
        updateBulkActions();
    });
    
    function updateBulkActions() {
        const checkedCount = $('.message-checkbox:checked').length;
        $('.bulk-action-btn').prop('disabled', checkedCount === 0);
        $('#selected-count').text(checkedCount);
    }
    
    // Real-time notifications
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
    
    // Websocket connection for real-time updates
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const messageSocket = new WebSocket(
        ws_scheme + '://' + window.location.host + '/ws/messages/'
    );
    
    messageSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'new_message') {
            updateUnreadCount(data.unread_count);
            showNotification(data.message);
        }
    };
    
    function updateUnreadCount(count) {
        const badge = document.querySelector('.message-count-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }
    
    function showNotification(message) {
        if (Notification.permission === 'granted') {
            new Notification('New Message', {
                body: `From: ${message.sender}\nSubject: ${message.subject}`,
                icon: '/static/img/logo.png'
            });
        }
    }
});
</script>
{% endblock %}{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Compose Message{% endblock %}

{% block page_specific_css %}
<style>
    /* Select2 Bootstrap 5 Compatibility */
    .select2-container--default .select2-selection--multiple,
    .select2-container--default .select2-selection--single {
        border: 1px solid #ced4da;
        border-radius: 0.25rem;
    }
    
    .select2-container {
        width: 100% !important;
    }

    /* Fix for double cancel button */
    .btn-cancel-mobile {
        display: none;
    }

    @media (max-width: 768px) {
        .btn-cancel-desktop {
            display: none;
        }
        .btn-cancel-mobile {
            display: inline-block;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title h5 mb-0">
                        {% if is_reply %}Reply
                        {% elif is_reply_all %}Reply All
                        {% elif is_forward %}Forward
                        {% else %}Compose Message
                        {% endif %}
                    </h2>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data" id="compose-form" novalidate>
                        {% csrf_token %}
                        
                        {# Subject Field #}
                        {{ form.subject|as_crispy_field }}

                        {# Recipients Fields #}
                        <div class="mb-3">
                            <label for="id_recipients" class="form-label required">To</label>
                            {{ form.recipients }}
                            <div class="invalid-feedback" id="recipients-error" style="display: none;">
                                Please select at least one recipient.
                            </div>
                        </div>

                        {# CC and BCC Fields #}
                        <div class="mb-3">
                            <label for="id_cc" class="form-label">CC</label>
                            {{ form.cc }}
                        </div>
                        <div class="mb-3">
                            <label for="id_bcc" class="form-label">BCC</label>
                            {{ form.bcc }}
                        </div>

                        {# Related Study Field #}
                        {{ form.related_submission|as_crispy_field }}
                        <small class="text-muted d-block mt-1 mb-3">Search by study title or IRB number</small>

                        {# Message Body #}
                        {{ form.body|as_crispy_field }}

                        {# Attachments #}
                        <div class="mb-3">
                            <label for="id_attachment" class="form-label">Attachment</label>
                            {{ form.attachment }}
                            <small class="text-muted d-block mt-1" id="file-name-display">Select a file to attach</small>
                        </div>

                        {# Submit Buttons #}
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                            <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary me-md-2 btn-cancel-desktop">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                            <button type="submit" class="btn btn-primary" id="send-button">
                                <i class="fas fa-paper-plane"></i> Send
                            </button>
                            <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary btn-cancel-mobile">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
$(document).ready(function() {
    // Initialize Select2 for recipients fields
    function initializeSelect2(element, url, placeholder) {
        return $(element).select2({
            theme: 'bootstrap5',
            ajax: {
                url: url,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page || 1
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.label
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: placeholder,
            allowClear: true,
            multiple: true,
            width: '100%'
        });
    }

    // Initialize recipients fields
    const recipientsSelect = initializeSelect2('#id_recipients', '{% url "messaging:user_autocomplete" %}', 'Select recipients...');
    const ccSelect = initializeSelect2('#id_cc', '{% url "messaging:user_autocomplete" %}', 'Select CC recipients...');
    const bccSelect = initializeSelect2('#id_bcc', '{% url "messaging:user_autocomplete" %}', 'Select BCC recipients...');

    // Initialize related submission field
    $('#id_related_submission').select2({
        theme: 'bootstrap5',
        ajax: {
            url: '{% url "messaging:submission_autocomplete" %}',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    term: params.term,
                    page: params.page || 1
                };
            },
            processResults: function (data) {
                return {
                    results: data.map(function(item) {
                        return {
                            id: item.id,
                            text: `${item.title} (${item.irb_number || 'No IRB'})`
                        };
                    })
                };
            },
            cache: true
        },
        minimumInputLength: 2,
        placeholder: 'Search for a study...',
        allowClear: true,
        width: '100%'
    });

    // Handle initial values
    {% if form.recipients.initial %}
        var initialRecipients = {{ form.recipients.initial|safe }};
        initialRecipients.forEach(function(user) {
            var option = new Option(user.text, user.id, true, true);
            $('#id_recipients').append(option);
        });
        $('#id_recipients').trigger('change');
    {% endif %}

    {% if form.related_submission.initial %}
        var initialSubmission = {
            id: '{{ form.related_submission.initial.id }}',
            text: '{{ form.related_submission.initial.title|escapejs }}'
        };
        var option = new Option(initialSubmission.text, initialSubmission.id, true, true);
        $('#id_related_submission').append(option).trigger('change');
    {% endif %}

    // File attachment handling
    $('#id_attachment').on('change', function() {
        var fileName = this.files[0]?.name || 'Select a file to attach';
        $('#file-name-display').text(fileName);
    });

    // Form submission handling
    $('#compose-form').on('submit', function(e) {
        e.preventDefault();
        
        // Clear previous error states
        $('#recipients-error').hide();
        $('.is-invalid').removeClass('is-invalid');
        
        // Validate recipients
        const recipients = $('#id_recipients').val();
        if (!recipients || recipients.length === 0) {
            $('#id_recipients').next('.select2-container').find('.select2-selection').addClass('is-invalid');
            $('#recipients-error').show();
            return false;
        }

        // If validation passes, submit the form
        this.submit();
    });

    // Clear invalid state when recipients are selected
    $('#id_recipients').on('change', function() {
        if ($(this).val()?.length > 0) {
            $(this).next('.select2-container').find('.select2-selection').removeClass('is-invalid');
            $('#recipients-error').hide();
        }
    });
});
</script>
{% endblock %}{% extends 'users/base.html' %}
{% load static %}
{% load messaging_extras %}
{% load message_tags %}

{% block title %}Inbox{% endblock %}

{% block page_specific_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap5.min.css">
<style>
    /* Container adjustments */
    .messages-container {
        max-width: 100%;
        overflow-x: hidden;
        padding: 0;
    }

    /* Table width control */
    .table-responsive {
        margin: 0;
        padding: 0;
        width: 100%;
    }

    #messages-table {
        width: 100% !important;
    }

    /* Column width controls */
    .checkbox-column { 
        width: 40px; 
        min-width: 40px;
    }
    .status-column { 
        width: 80px; 
        min-width: 80px;
        color: rgb(0, 0, 0); /* Ensure the status column text is visible */
    }
    .recipient-column { 
        width: 150px; 
        min-width: 150px;
    }
    .date-column { 
        width: 120px; 
        min-width: 120px;
    }
    .subject-column {
        min-width: 200px;
    }
    .study-column {
        min-width: 150px;
    }

    /* Truncate long text */
    .message-link {
        display: block;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: inherit;
        text-decoration: none;
    }

    .message-link:hover {
        color: #0d6efd;
    }

    .form-check-input {
        opacity: 1 !important;
        position: static !important;
        margin-left: 0 !important;
        cursor: pointer;
    }

    .badge.badge-sent {
        background-color: #198754;
        color: white;
    }

    .badge.badge-archived {
        background-color: #6c757d;
        color: white;
    }

    .action-buttons {
        margin-bottom: 1rem;
    }

    .action-buttons .btn {
        margin-right: 0.5rem;
    }

    /* DataTables responsive adjustments */
    .dataTables_wrapper .row {
        margin: 0;
        padding: 0.5rem 0;
    }

    .dataTables_wrapper .dataTables_length,
    .dataTables_wrapper .dataTables_filter {
        padding: 0 0.5rem;
    }

    /* Card adjustments */
    .card {
        margin: 0;
        border-radius: 0.5rem;
    }

    .card-body {
        padding: 1rem;
    }

    @media (max-width: 768px) {
        .action-buttons .btn {
            margin-bottom: 0.5rem;
        }
        
        .date-column small {
            display: none;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="table-container">
        <div class="row mb-4">
            <div class="col">
                <h1 class="h3">Inbox</h1>
            </div>
            <div class="col-auto">
                <a href="{% url 'messaging:compose_message' %}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> New Message
                </a>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                <!-- Action Buttons -->
                <div class="action-buttons">
                    <button type="button" class="btn btn-warning btn-sm" id="archive-selected" disabled>
                        <i class="fas fa-archive"></i> Archive Selected
                    </button>
                    <button type="button" class="btn btn-secondary btn-sm" id="mark-read" disabled>
                        <i class="fas fa-check-double"></i> Mark as Read
                    </button>
                    <button type="button" class="btn btn-secondary btn-sm" id="mark-unread" disabled>
                        <i class="fas fa-check"></i> Mark as Unread
                    </button>
                </div>

                <!-- Messages Table -->
                <div class="table-responsive">
                    <table id="inbox-table" class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th class="checkbox-column">
                                    <input type="checkbox" class="form-check-input" id="select-all">
                                </th>
                                <th class="status-column">Status</th>
                                <th class="sender-column">From</th>
                                <th>Subject</th>
                                <th>Study Name</th>
                                <th class="date-column">Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for message in messages %}
                            <tr class="{% if not message|get_read_status:request.user %}unread-message{% endif %}" 
                                data-message-id="{{ message.id }}">
                                <td>
                                    <input type="checkbox" class="form-check-input message-checkbox" 
                                           value="{{ message.id }}">
                                </td>
                                <td class="text-center">
                                    {% if message|get_read_status:request.user %}
                                        <span class="badge badge-read">Read</span>
                                    {% else %}
                                        <span class="badge badge-unread">Unread</span>
                                    {% endif %}
                                </td>
                                <td>{{ message.sender.get_full_name|default:message.sender.username }}</td>
                                <td>
                                    <a href="{% url 'messaging:view_message' message.id %}" class="message-link">
                                        {{ message.subject }}
                                        {% if message.attachments.exists %}
                                            <i class="fas fa-paperclip text-muted"></i>
                                        {% endif %}
                                    </a>
                                </td>
                                <td>{{ message.study_name|default:"-" }}</td>
                                <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">
                                    {{ message.sent_at|date:"M d, Y" }}
                                    <br>
                                    <small class="text-muted">{{ message.sent_at|date:"H:i" }}</small>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="6" class="text-center py-4">
                                    <p class="text-muted mb-0">Your inbox is empty</p>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<!-- DataTables JS -->
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap5.min.js"></script>

<script>
$(document).ready(function() {
    // Initialize DataTable
    const table = $('#inbox-table').DataTable({
        order: [[5, "desc"]],
        pageLength: 25,
        columnDefs: [
            { orderable: false, targets: [0, 1] }
        ],
        language: {
            emptyTable: "No messages in your inbox",
            zeroRecords: "No messages found matching your search"
        }
    });

    // Select All Functionality
    $('#select-all').on('click', function() {
        $('.message-checkbox').prop('checked', this.checked);
        updateActionButtons();
    });

    // Individual Checkbox Functionality
    $(document).on('change', '.message-checkbox', function() {
        const allChecked = $('.message-checkbox:not(:checked)').length === 0;
        const anyChecked = $('.message-checkbox:checked').length > 0;
        $('#select-all').prop('checked', allChecked && anyChecked);
        updateActionButtons();
    });

    // Update Action Buttons State
    function updateActionButtons() {
        const selectedCount = $('.message-checkbox:checked').length;
        $('#archive-selected, #mark-read, #mark-unread').prop('disabled', selectedCount === 0);
        
        $('#archive-selected').html(
            `<i class="fas fa-archive"></i> Archive Selected${selectedCount > 0 ? ` (${selectedCount})` : ''}`
        );
    }

    // Handle Archive Action
    $('#archive-selected').on('click', function() {
        const selectedIds = $('.message-checkbox:checked').map(function() {
            return $(this).val();
        }).get();

        if (selectedIds.length === 0) return;

        if (confirm(`Are you sure you want to archive ${selectedIds.length} message(s)?`)) {
            $.ajax({
                url: '{% url "messaging:archive_message" %}',
                type: 'POST',
                data: {
                    selected_messages: selectedIds,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    } else {
                        showNotification('Error archiving messages', 'error');
                    }
                }
            });
        }
    });

    // Handle Mark Read/Unread
    $('#mark-read, #mark-unread').on('click', function() {
        const isMarkRead = $(this).attr('id') === 'mark-read';
        const selectedIds = $('.message-checkbox:checked').map(function() {
            return $(this).val();
        }).get();

        if (selectedIds.length === 0) return;

        $.ajax({
            url: '{% url "messaging:update_read_status" %}',
            type: 'POST',
            data: {
                message_ids: selectedIds,
                is_read: isMarkRead,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function(response) {
                if (response.status === 'success') {
                    location.reload();
                } else {
                    showNotification('Error updating message status', 'error');
                }
            }
        });
    });

    // Initial button state update
    updateActionButtons();
});
</script>
{% endblock %}<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .message-meta {
            margin-bottom: 20px;
            font-size: 14px;
        }
        .message-meta div {
            margin-bottom: 5px;
        }
        .message-body {
            padding: 15px;
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        }
        .btn-view {
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }
        .attachments {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .footer {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h2>{{ message.subject }}</h2>
    </div>

    <div class="message-meta">
        <div><strong>From:</strong> {{ sender.get_full_name|default:sender.email }}</div>
        {% if message.recipients.all %}
        <div><strong>To:</strong> {{ message.recipients.all|join:", " }}</div>
        {% endif %}
        {% if message.cc.all %}
        <div><strong>CC:</strong> {{ message.cc.all|join:", " }}</div>
        {% endif %}
        {% if message.study_name %}
        <div><strong>Study:</strong> {{ message.study_name }}</div>
        {% endif %}
    </div>

    <div class="message-body">
        {{ message.body|linebreaks }}
    </div>

    {% if message.attachments.all %}
    <div class="attachments">
        <h4>Attachments:</h4>
        <ul>
            {% for attachment in message.attachments.all %}
            <li>{{ attachment.filename }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    <a href="{{ view_url }}" class="btn-view">View Message in Platform</a>

    <div class="footer">
        <p>This is an automated message from your messaging system. Please do not reply to this email.</p>
        <p>To respond to this message, please use the platform's messaging system.</p>
    </div>
</body>
</html>{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Search Results{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Search Results for "{{ query }}"</h1>
    
    {% if messages %}
        <div class="table-responsive">
            <table id="search-results-table" class="table table-striped table-hover">
                <thead class="thead-light">
                    <tr>
                        <th>From</th>
                        <th>To</th>
                        <th>Subject</th>
                        <th>Study Name</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td>{{ message.sender.username }}</td>
                        <td>{{ message.recipients.all|join:", " }}</td>
                        <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                        <td>{{ message.study_name|default_if_none:"-" }}</td>
                        <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <p>No messages found matching your search query.</p>
    {% endif %}
    
    <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary mt-3">Back to Inbox</a>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        $('#search-results-table').DataTable({
            "order": [[4, "desc"]]
        });
    });
</script>
{% endblock %}
{# sent_messages.html #}
{% extends 'users/base.html' %}
{% load static %}
{% load messaging_extras %}
{% load message_tags %}

{% block title %}Sent Messages{% endblock %}

{% block page_specific_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap5.min.css">
<style>
    /* Container adjustments */
    .messages-container {
        max-width: 100%;
        overflow-x: hidden;
        padding: 0;
    }

    /* Table width control */
    .table-responsive {
        margin: 0;
        padding: 0;
        width: 100%;
    }

    #messages-table {
        width: 100% !important;
    }

    /* Column width controls */
    .checkbox-column { 
        width: 40px; 
        min-width: 40px;
    }
    .status-column { 
        width: 80px; 
        min-width: 80px;
    }
    .recipient-column { 
        width: 150px; 
        min-width: 150px;
    }
    .date-column { 
        width: 120px; 
        min-width: 120px;
    }
    .subject-column {
        min-width: 200px;
    }
    .study-column {
        min-width: 150px;
    }

    /* Truncate long text */
    .message-link {
        display: block;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: inherit;
        text-decoration: none;
    }

    .message-link:hover {
        color: #0d6efd;
    }

    .form-check-input {
        opacity: 1 !important;
        position: static !important;
        margin-left: 0 !important;
        cursor: pointer;
    }

    .badge.badge-sent {
        background-color: #198754;
        color: white;
    }

    .badge.badge-archived {
        background-color: #6c757d;
        color: white;
    }

    .action-buttons {
        margin-bottom: 1rem;
    }

    .action-buttons .btn {
        margin-right: 0.5rem;
    }

    /* DataTables responsive adjustments */
    .dataTables_wrapper .row {
        margin: 0;
        padding: 0.5rem 0;
    }

    .dataTables_wrapper .dataTables_length,
    .dataTables_wrapper .dataTables_filter {
        padding: 0 0.5rem;
    }

    /* Card adjustments */
    .card {
        margin: 0;
        border-radius: 0.5rem;
    }

    .card-body {
        padding: 1rem;
    }

    @media (max-width: 768px) {
        .action-buttons .btn {
            margin-bottom: 0.5rem;
        }
        
        .date-column small {
            display: none;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="messages-container">
    <div class="row mb-4">
        <div class="col">
            <h1 class="h3">{% if is_archived %}Archived Messages{% else %}Sent Messages{% endif %}</h1>
        </div>
        <div class="col-auto">
            <a href="{% url 'messaging:compose_message' %}" class="btn btn-primary">
                <i class="fas fa-plus"></i> New Message
            </a>
        </div>
    </div>

    <div class="card">
        <div class="card-body">
            {% if not is_archived %}
            <div class="action-buttons">
                <button type="button" class="btn btn-warning btn-sm" id="archive-selected" disabled>
                    <i class="fas fa-archive"></i> Archive Selected
                </button>
            </div>
            {% endif %}

            <div class="table-responsive">
                <table id="messages-table" class="table table-striped table-hover">
                    <thead>
                        <tr>
                            {% if not is_archived %}
                            <th class="checkbox-column">
                                <input type="checkbox" class="form-check-input" id="select-all">
                            </th>
                            {% endif %}
                            <th class="recipient-column">To</th>
                            <th class="subject-column">Subject</th>
                            <th class="study-column">Study Name</th>
                            <th class="date-column">Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for message in messages %}
                        <tr data-message-id="{{ message.id }}">
                            {% if not is_archived %}
                            <td class="checkbox-column">
                                <input type="checkbox" class="form-check-input message-checkbox" 
                                       value="{{ message.id }}">
                            </td>
                            {% endif %}
                            <td class="recipient-column">
                                <span class="text-truncate">
                                    {{ message.get_recipients_display }}
                                </span>
                            </td>
                            <td class="subject-column">
                                <a href="{% url 'messaging:view_message' message.id %}" class="message-link">
                                    {{ message.subject }}
                                    {% if message.attachments.exists %}
                                        <i class="fas fa-paperclip text-muted"></i>
                                    {% endif %}
                                </a>
                            </td>
                            <td class="study-column">
                                <span class="text-truncate">{{ message.study_name|default:"-" }}</span>
                            </td>
                            <td class="date-column" data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">
                                {{ message.sent_at|date:"M d, Y" }}
                                <small class="text-muted d-block">{{ message.sent_at|date:"H:i" }}</small>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="{% if is_archived %}4{% else %}5{% endif %}" class="text-center py-4">
                                <p class="text-muted mb-0">
                                    {% if is_archived %}
                                        No archived messages
                                    {% else %}
                                        No sent messages
                                    {% endif %}
                                </p>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap5.min.js"></script>

<script>
$(document).ready(function() {
    // Initialize DataTable
    const table = $('#messages-table').DataTable({
        order: [[{% if is_archived %}3{% else %}4{% endif %}, "desc"]],
        pageLength: 25,
        columnDefs: [
            {% if not is_archived %}
            { orderable: false, targets: [0] },
            {% endif %}
        ],
        language: {
            emptyTable: "No messages to display",
            zeroRecords: "No messages found matching your search"
        },
        dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rtip'
    });

    {% if not is_archived %}
    // Select All Functionality
    $('#select-all').on('click', function() {
        $('.message-checkbox').prop('checked', this.checked);
        updateActionButtons();
    });

    // Individual Checkbox Functionality
    $(document).on('change', '.message-checkbox', function() {
        const allChecked = $('.message-checkbox:not(:checked)').length === 0;
        const anyChecked = $('.message-checkbox:checked').length > 0;
        $('#select-all').prop('checked', allChecked && anyChecked);
        updateActionButtons();
    });

    // Update Action Buttons State
    function updateActionButtons() {
        const selectedCount = $('.message-checkbox:checked').length;
        $('#archive-selected').prop('disabled', selectedCount === 0);
        
        $('#archive-selected').html(
            `<i class="fas fa-archive"></i> Archive Selected${selectedCount > 0 ? ` (${selectedCount})` : ''}`
        );
    }

    // Handle Archive Action
    $('#archive-selected').on('click', function() {
        const selectedIds = $('.message-checkbox:checked').map(function() {
            return $(this).val();
        }).get();

        if (selectedIds.length === 0) return;

        if (confirm(`Are you sure you want to archive ${selectedIds.length} message(s)?`)) {
            $.ajax({
                url: '{% url "messaging:archive_message" %}',
                type: 'POST',
                data: {
                    selected_messages: selectedIds,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function(response) {
                    if (response.status === 'success') {
                        location.reload();
                    } else {
                        showNotification('Error archiving messages', 'error');
                    }
                }
            });
        }
    });

    // Initial button state update
    updateActionButtons();
    {% endif %}
});
</script>
{% endblock %}{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Threads Inbox{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Threads Inbox</h1>
    
    <div class="table-responsive">
        <table id="threads-table" class="table table-striped table-hover">
            <thead class="thead-light">
                <tr>
                    <th>From</th>
                    <th>Subject</th>
                    <th>Study Name</th>
                    <th>Thread Size</th>
                    <th>Started</th>
                    <th>Last Update</th>
                </tr>
            </thead>
            <tbody>
                {% for message in first_messages %}
                <tr>
                    <td>{{ message.sender.username }}</td>
                    <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                    <td>{{ message.study_name|default_if_none:"-" }}</td>
                    <td>{{ message.thread_size }}</td>
                    <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    <td data-order="{{ message.last_update|date:'Y-m-d H:i:s' }}">{{ message.last_update|date:"M d, Y H:i" }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        $('#threads-table').DataTable({
            "order": [[5, "desc"]], // Sort by last update by default
            "pageLength": 25,
            "language": {
                "emptyTable": "No threads with more than one message found."
            }
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}{{ message.subject }}{% endblock %}

{% block page_specific_css %}
<style>
    .message-container {
        max-width: 100%;
        padding: 0;
    }

    .message-header {
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        padding: 1.5rem;
    }

    .message-subject {
        font-size: 1.5rem;
        font-weight: 500;
        color: #212529;
        margin-bottom: 1.5rem;
    }

    .message-meta {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 0.5rem 1.5rem;
        align-items: start;
    }

    .message-meta-label {
        color: #6c757d;
        font-weight: 500;
        white-space: nowrap;
    }

    .message-meta-content {
        color: #212529;
        word-break: break-word;
    }

    .message-body {
        padding: 2rem;
        white-space: pre-wrap;
        color: #212529;
        min-height: 200px;
        background-color: white;
    }

    .message-footer {
        background-color: #f8f9fa;
        border-top: 1px solid #dee2e6;
        padding: 1rem;
    }

    .attachment-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .attachment-item {
        display: inline-flex;
        align-items: center;
        background-color: #e9ecef;
        border-radius: 4px;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        font-size: 0.875rem;
    }

    .attachment-item i {
        margin-right: 0.5rem;
        color: #6c757d;
    }

    .attachment-item a {
        color: #495057;
        text-decoration: none;
    }

    .attachment-item a:hover {
        color: #0d6efd;
    }

    .message-actions {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .message-actions .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
    }

    .navigation-actions {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }

    .recipient-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .recipient-chip {
        background-color: #e9ecef;
        border-radius: 16px;
        padding: 0.25rem 0.75rem;
        font-size: 0.875rem;
    }

    @media (max-width: 768px) {
        .message-meta {
            grid-template-columns: 1fr;
            gap: 0.75rem;
        }
        
        .message-actions {
            flex-direction: column;
        }
        
        .message-actions .btn {
            width: 100%;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="message-container">
    <div class="card">
        <div class="message-header">
            <h1 class="message-subject">{{ message.subject }}</h1>
            
            <div class="message-meta">
                <span class="message-meta-label">From</span>
                <span class="message-meta-content">
                    {{ message.sender.get_full_name|default:message.sender.username }}
                    <small class="text-muted">&lt;{{ message.sender.email }}&gt;</small>
                </span>

                <span class="message-meta-label">To</span>
                <div class="message-meta-content recipient-list">
                    {% for recipient in message.recipients.all %}
                        <span class="recipient-chip">
                            {{ recipient.get_full_name|default:recipient.username }}
                        </span>
                    {% endfor %}
                </div>

                {% if message.cc.all %}
                    <span class="message-meta-label">CC</span>
                    <div class="message-meta-content recipient-list">
                        {% for cc in message.cc.all %}
                            <span class="recipient-chip">
                                {{ cc.get_full_name|default:cc.username }}
                            </span>
                        {% endfor %}
                    </div>
                {% endif %}

                {% if message.bcc.all and user == message.sender %}
                    <span class="message-meta-label">BCC</span>
                    <div class="message-meta-content recipient-list">
                        {% for bcc in message.bcc.all %}
                            <span class="recipient-chip">
                                {{ bcc.get_full_name|default:bcc.username }}
                            </span>
                        {% endfor %}
                    </div>
                {% endif %}

                <span class="message-meta-label">Date</span>
                <span class="message-meta-content">
                    {{ message.sent_at|date:"l, F j, Y" }}
                    <small class="text-muted">at {{ message.sent_at|date:"g:i A" }}</small>
                </span>

                {% if message.study_name %}
                    <span class="message-meta-label">Study</span>
                    <span class="message-meta-content">{{ message.study_name }}</span>
                {% endif %}

                {% if message.attachments.all %}
                    <span class="message-meta-label">Attachments</span>
                    <div class="message-meta-content">
                        <ul class="attachment-list">
                            {% for attachment in message.attachments.all %}
                                <li class="attachment-item">
                                    <i class="fas fa-paperclip"></i>
                                    <a href="{{ attachment.file.url }}" target="_blank" download>
                                        {{ attachment.filename }}
                                    </a>
                                </li>
                            {% endfor %}
                        </ul>
                    </div>
                {% endif %}

                {% if message.hashtags.all %}
                    <span class="message-meta-label">Tags</span>
                    <div class="message-meta-content">
                        {% for tag in message.hashtags.all %}
                            <span class="badge bg-secondary">{{ tag }}</span>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </div>

        <div class="message-body">
            {{ message.body|linebreaks }}
        </div>

        <div class="message-footer">
            <div class="message-actions">
                <a href="{% url 'messaging:reply' message.id %}" class="btn btn-primary">
                    <i class="fas fa-reply"></i>
                    Reply
                </a>
                <a href="{% url 'messaging:reply_all' message.id %}" class="btn btn-secondary">
                    <i class="fas fa-reply-all"></i>
                    Reply All
                </a>
                <a href="{% url 'messaging:forward' message.id %}" class="btn btn-info">
                    <i class="fas fa-share"></i>
                    Forward
                </a>
                
                <form method="post" action="{% url 'messaging:archive_message' %}" class="d-inline">
                    {% csrf_token %}
                    <input type="hidden" name="selected_messages" value="{{ message.id }}">
                    <button type="submit" class="btn {% if user == message.sender %}btn-danger{% else %}btn-warning{% endif %}"
                            onclick="return confirm('Are you sure you want to archive this message?');">
                        <i class="fas fa-archive"></i>
                        Archive
                    </button>
                </form>
            </div>
        </div>
    </div>

    <div class="navigation-actions">
        <a href="javascript:history.back()" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i>
            Back
        </a>
        <a href="{% url 'messaging:inbox' %}" class="btn btn-primary">
            <i class="fas fa-inbox"></i>
            Go to Inbox
        </a>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
$(document).ready(function() {
    // Prevent notifications on message view
    const originalShowNotification = window.showNotification;
    window.showNotification = function(message, type) {
        // Do nothing - suppress notifications
    };
});
</script>
{% endblock %}