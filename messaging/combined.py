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
                outfile.write(line)from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from submission.models import Submission
from .models import Message, MessageAttachment

class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    bcc = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
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
            'data-placeholder': 'Search for a submission...'
        })
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Message
        fields = ['recipients', 'cc', 'bcc', 'subject', 'body', 'related_submission']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            accessible_submissions = Submission.objects.filter(
                Q(primary_investigator=user) |
                Q(coinvestigator__user=user) |  # Changed to look up through the user field
                Q(researchassistant__user=user)  # Changed to look up through the user field
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
    thread_id = models.UUIDField(default=uuid.uuid4, editable=False)
    related_submission = models.ForeignKey(
        'submission.Submission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_messages'
    )
    
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
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, MessageReadStatus

@receiver(post_save, sender='messaging.Message')
def create_message_read_status(sender, instance, created, **kwargs):
    if created:
        from .models import MessageReadStatus
        for recipient in instance.recipients.all():
            MessageReadStatus.objects.create(user=recipient, message=instance)

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
]
# messaging/validators.py

from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_kb = 10240  # 10 MB
    if value.size > max_kb * 1024:
        raise ValidationError('Maximum file size is 10 MB')
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from .models import Message, MessageReadStatus, Comment, MessageAttachment
from .forms import MessageForm, SearchForm
from submission.models import Submission

User = get_user_model()

@login_required
def inbox(request):
    messages_list = Message.objects.filter(recipients=request.user, is_archived=False).order_by('-sent_at')
    return render(request, 'messaging/inbox.html', {'messages': messages_list})

@login_required
def sent_messages(request):
    messages_list = Message.objects.filter(sender=request.user).order_by('-sent_at')
    return render(request, 'messaging/sent_messages.html', {'messages': messages_list})

@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    return render(request, 'messaging/view_message.html', {'message': message})

@login_required
def compose_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # Save many-to-many relationships after saving the message
            form.save_m2m()
            
            messages.success(request, 'Message sent successfully!')
            return redirect('messaging:inbox')
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
def archive_message(request):
    if request.method == 'POST':
        message_ids = request.POST.getlist('selected_messages')
        Message.objects.filter(id__in=message_ids, recipients=request.user).update(is_archived=True)
        messages.success(request, f"{len(message_ids)} messages archived.")
    return redirect('messaging:inbox')

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
def submission_autocomplete(request):
    """View for handling submission autocomplete requests"""
    term = request.GET.get('term', '')
    user = request.user
    
    # Query submissions that the user has access to
    submissions = Submission.objects.filter(
        Q(primary_investigator=user) |
        Q(coinvestigator__user=user) |
        Q(research_assistants__user=user),
        Q(title__icontains=term) |
        Q(irb_number__icontains=term)
    ).distinct()[:10]

    results = []
    for submission in submissions:
        label = f"{submission.title}"
        if submission.irb_number:
            label += f" (IRB: {submission.irb_number})"
        results.append({
            'id': submission.temporary_id,
            'text': label
        })

    return JsonResponse({'results': results}, safe=False)
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
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Compose Message{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>
                        {% if is_reply %}Reply
                        {% elif is_reply_all %}Reply All
                        {% elif is_forward %}Forward
                        {% else %}Compose Message
                        {% endif %}
                    </h2>
                </div>
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data" novalidate>
                        {% csrf_token %}
                        
                        {# Subject Field #}
                        {{ form.subject|as_crispy_field }}

                        {# Related Study Field #}
                        {{ form.related_submission|as_crispy_field }}
                        <small class="text-muted d-block mt-1 mb-3">Search by study title or IRB number</small>

                        {# Recipients Fields #}
                        {{ form.recipients|as_crispy_field }}
                        {{ form.cc|as_crispy_field }}
                        {{ form.bcc|as_crispy_field }}

                        {# Message Body #}
                        {{ form.body|as_crispy_field }}

                        {# Attachments #}
                        {{ form.attachment|as_crispy_field }}
                        <small class="text-muted d-block mt-1 mb-3">Select a file to attach</small>

                        {# Submit Buttons #}
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                            <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary me-md-2">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                            <button type="submit" class="btn btn-primary">Send</button>
                            <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary">Cancel</a>
                            </button>
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
        // Initialize Select2 for recipients, cc, and bcc fields
        $('#id_recipients, #id_cc, #id_bcc').select2({
            theme: 'bootstrap4',
            ajax: {
                url: '{% url "messaging:user_autocomplete" %}',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page
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
            placeholder: 'Search for users...',
            allowClear: true,
            multiple: true,
            width: '100%'
        });

        // Initialize Select2 for related submission field
        $('#id_related_submission').select2({
            theme: 'bootstrap4',
            ajax: {
                url: '{% url "messaging:submission_autocomplete" %}',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page
                    };
                },
                processResults: function (data) {
                    return data;
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: 'Search for a study...',
            allowClear: true,
            multiple: false,
            width: '100%'
        });

        // Handle initial values if they exist
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
            var initialOption = new Option(initialSubmission.text, initialSubmission.id, true, true);
            $('#id_related_submission').append(initialOption).trigger('change');
        {% endif %}

        // Optional: Show selected file name
        $('#id_attachment').on('change', function() {
            var fileName = $(this).val().split('\\').pop();
            $(this).next('.text-muted').text(fileName || 'Select a file to attach');
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Inbox{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Inbox</h1>
    
    <form method="post" action="{% url 'messaging:archive_message' %}">
        {% csrf_token %}
        <div class="table-responsive">
            <table id="inbox-table" class="table table-striped table-hover">
                <thead class="thead-light">
                    <tr>
                        <th><input type="checkbox" id="select-all"></th>
                        <th>Status</th>
                        <th>From</th>
                        <th>Subject</th>
                        <th>Study Name</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td><input type="checkbox" name="selected_messages" value="{{ message.id }}"></td>
                        <td>{% if message|get_read_status:request.user %}<span class="badge badge-secondary">Read</span>{% else %}<span class="badge badge-primary">Unread</span>{% endif %}</td>
                        <td>{{ message.sender.username }}</td>
                        <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                        <td>{{ message.study_name|default_if_none:"-" }}</td>
                        <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <button type="submit" class="btn btn-warning mt-3">Archive Selected</button>
    </form>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        var table = $('#inbox-table').DataTable({
            "order": [[5, "desc"]],
            "columnDefs": [
                { "orderable": false, "targets": [0, 1] }
            ]
        });

        $('#select-all').on('click', function(){
            $('input[name="selected_messages"]').prop('checked', this.checked);
        });

        $('input[name="selected_messages"]').on('change', function(){
            $('#select-all').prop('checked', $('input[name="selected_messages"]:checked').length === $('input[name="selected_messages"]').length);
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
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
{% extends 'users/base.html' %}
{% load messaging_extras %}

{% block title %}Sent Messages{% endblock %}

{% block extra_css %}
{{ block.super }}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Sent Messages</h1>
    
    <form method="post" action="{% url 'messaging:archive_message' %}">
        {% csrf_token %}
        <div class="table-responsive">
            <table id="sent-messages-table" class="table table-striped table-hover">
                <thead class="thead-light">
                    <tr>
                        <th><input type="checkbox" id="select-all"></th>
                        <th>To</th>
                        <th>Subject</th>
                        <th>Study Name</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for message in messages %}
                    <tr>
                        <td><input type="checkbox" name="selected_messages" value="{{ message.id }}"></td>
                        <td>{{ message.recipients.all|join:", " }}</td>
                        <td><a href="{% url 'messaging:view_message' message.id %}">{{ message.subject }}</a></td>
                        <td>{{ message.study_name|default_if_none:"-" }}</td>
                        <td data-order="{{ message.sent_at|date:'Y-m-d H:i:s' }}">{{ message.sent_at|date:"M d, Y H:i" }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <button type="submit" class="btn btn-warning mt-3">Archive Selected</button>
    </form>
</div>
{% endblock %}

{% block extra_js %}
{{ block.super }}
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>
<script>
    $(document).ready(function() {
        var table = $('#sent-messages-table').DataTable({
            "order": [[4, "desc"]],
            "columnDefs": [
                { "orderable": false, "targets": 0 }
            ]
        });

        $('#select-all').on('click', function(){
            $('input[name="selected_messages"]').prop('checked', this.checked);
        });

        $('input[name="selected_messages"]').on('change', function(){
            $('#select-all').prop('checked', $('input[name="selected_messages"]:checked').length === $('input[name="selected_messages"]').length);
        });
    });
</script>
{% endblock %}
{% extends 'users/base.html' %}
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

{% block title %}View Message{% endblock %}

{% block extra_css %}
{{ block.super }}
<style>
    .message-header {
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        padding: 15px;
    }
    .message-body {
        padding: 20px;
        white-space: pre-wrap;
    }
    .message-footer {
        background-color: #f8f9fa;
        border-top: 1px solid #dee2e6;
        padding: 15px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header message-header">
            <h2 class="mb-3">{{ message.subject }}</h2>
            <div class="row">
                <div class="col-md-6">
                    <p><strong>From:</strong> {{ message.sender.username }}</p>
                    <p><strong>To:</strong> {{ message.recipients.all|join:", " }}</p>
                    {% if message.cc.all %}
                        <p><strong>CC:</strong> {{ message.cc.all|join:", " }}</p>
                    {% endif %}
                    {% if message.bcc.all %}
                        <p><strong>BCC:</strong> {{ message.bcc.all|join:", " }}</p>
                    {% endif %}
                    {% if message.study_name %}
                        <p><strong>Study Name:</strong> {{ message.study_name }}</p>
                    {% endif %}
                    <p><strong>Sent At:</strong> {{ message.sent_at|date:"F d, Y H:i" }}</p>
                    <p><strong>Attachments:</strong> 
                        {% if message.attachments.all %}
                            <ul class="list-unstyled">
                            {% for attachment in message.attachments.all %}
                                <li>
                                    <i class="fas fa-paperclip"></i>
                                    <a href="{{ attachment.file.url }}" target="_blank">
                                        {{ attachment.filename }}
                                    </a>
                                </li>
                            {% endfor %}
                            </ul>
                        {% else %}
                            None
                        {% endif %}
                    </p>
                    <p><strong>Hashtags:</strong> {% if message.hashtags.all %}{{ message.hashtags.all|join:", " }}{% else %}None{% endif %}</p>
                </div>
                <div class="col-md-6 text-md-right">
                    <p><strong>Date:</strong> {{ message.sent_at|date:"F d, Y H:i" }}</p>
                    <p><strong>Study Name:</strong> {{ message.study_name }}</p>
                </div>
            </div>
        </div>
        <div class="card-body message-body">
            {{ message.body|linebreaks }}
        </div>
        <div class="card-footer message-footer">
            <div class="btn-group" role="group">
                <a href="{% url 'messaging:reply' message.id %}" class="btn btn-primary">Reply</a>
                <a href="{% url 'messaging:reply_all' message.id %}" class="btn btn-secondary">Reply All</a>
                <a href="{% url 'messaging:forward' message.id %}" class="btn btn-info">Forward</a>
                {% if user == message.sender %}
                    <form method="post" action="{% url 'messaging:archive_message'%}" style="display: inline;">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-danger" onclick="return confirm('Are you sure you want to archive this message?');">Archive</button>
                    </form>
                {% else %}
                    <form method="post" action="{% url 'messaging:archive_message' %}" style="display: inline;">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-warning">Archive</button>
                    </form>
                {% endif %}
            </div>
        </div>
    </div>
    
    <a href="{% url 'messaging:inbox' %}" class="btn btn-secondary mt-3">Back to Inbox</a>
</div>
{% endblock %}
