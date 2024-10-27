# messaging/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Message, MessageReadStatus, Comment
from django.contrib.auth.decorators import login_required
from .forms import MessageForm, CommentForm, SearchForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages


@login_required
def inbox(request):
    messages = Message.objects.filter(recipients=request.user, is_archived=False).order_by('-sent_at')
    return render(request, 'messaging/inbox.html', {'messages': messages})

@login_required
def sent_messages(request):
    messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
    return render(request, 'messaging/sent_messages.html', {'messages': messages})

@login_required
def view_message(request, message_id):
    message = Message.objects.get(id=message_id)
    # Add logic to check if the user has permission to view this message
    return render(request, 'messaging/view_message.html', {'message': message})

@login_required
def compose_message(request):
    message = None  # Initialize 'message'
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('messaging:inbox')
    else:
        form = MessageForm()
    
    return render(request, 'messaging/compose_message.html', {'form': form})

@login_required
def reply_message(request, pk):
    original_message = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.subject = "Re: " + original_message.subject
            message.save()
            form.save_m2m()
            # Create read statuses
            for recipient in message.recipients.all():
                MessageReadStatus.objects.create(user=recipient, message=message)
            # Email notifications
            # ...
            return redirect('messaging:inbox')
    else:
        initial_data = {
            'recipients': original_message.recipients.all(),
            'subject': "Re: " + original_message.subject,
            'body': "\n\n--- Original Message ---\n" + original_message.body,
        }
        form = MessageForm(initial=initial_data)

    # Inside the compose_message and reply_message views

    # Email subject and body
    email_subject = message.subject
    email_body = message.body

    # Get recipient emails
    recipient_emails = [user.email for user in message.recipients.all()]

    # Send email
    send_mail(
        email_subject,
        email_body,
        settings.EMAIL_HOST_USER,
        recipient_emails,
        fail_silently=False,
    )

    return render(request, 'messaging/compose_message.html', {'form': form})

@login_required
def search_messages(request):
    query = request.GET.get('q', '')
    messages = []

    if query:
        messages = Message.objects.filter(
            Q(recipients=request.user) | Q(sender=request.user),
            Q(subject__icontains=query) | 
            Q(body__icontains=query) |
            Q(study_name__icontains=query)
        ).distinct().order_by('-sent_at')

    context = {
        'messages': messages,
        'query': query,
    }
    return render(request, 'messaging/search_results.html', context)


from dal import autocomplete

class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(username__icontains=self.q)
        return qs

@login_required
def archive_messages(request):
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
    messages = Message.objects.filter(recipients=request.user, is_archived=True).order_by('-sent_at')
    return render(request, 'messaging/archived_messages.html', {'messages': messages})
