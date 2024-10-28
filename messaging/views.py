# messaging/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Message, MessageReadStatus, Comment
from django.contrib.auth.decorators import login_required
from .forms import MessageForm, SearchForm
# from .forms import CommentForm
from django.contrib.auth.models import User
from django.db.models import Q, Count
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
    message = get_object_or_404(Message, id=message_id)
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
            'body': f"\n\nOn {original_message.sent_at}, {original_message.sender.username} wrote:\n{original_message.body}",
            'study_name': original_message.study_name,
            'recipients': [original_message.sender],
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
            new_message.save()
            new_message.recipients.add(original_message.sender)
            new_message.recipients.add(*original_message.recipients.exclude(id=request.user.id))
            new_message.cc.add(*original_message.cc.all())
            form.save_m2m()
            messages.success(request, 'Reply to all sent successfully.')
            return redirect('messaging:inbox')
    else:
        # Get all recipients excluding current user
        all_recipients = list(original_message.recipients.exclude(id=request.user.id))
        # Add original sender to recipients list
        all_recipients.append(original_message.sender)
        
        form = MessageForm(initial={
            'subject': f"Re: {original_message.subject}",
            'body': f"\n\nOn {original_message.sent_at}, {original_message.sender.username} wrote:\n{original_message.body}",
            'study_name': original_message.study_name,
            'recipients': all_recipients,
            'cc': original_message.cc.all(),
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
            'body': f"\n\n---------- Forwarded message ----------\nFrom: {original_message.sender.username}\nDate: {original_message.sent_at}\nSubject: {original_message.subject}\nTo: {', '.join([r.username for r in original_message.recipients.all()])}\n\n{original_message.body}",
            'study_name': original_message.study_name,
        })
    return render(request, 'messaging/compose_message.html', {'form': form, 'is_forward': True})

# @login_required
# def delete_message(request, message_id):
#     message = get_object_or_404(Message, id=message_id, sender=request.user)
#     if request.method == 'POST':
#         message.delete()
#         messages.success(request, 'Message deleted successfully.')
#     return redirect('messaging:inbox')

# @login_required
# def archive_message(request, message_id):
#     message = get_object_or_404(Message, id=message_id, recipients=request.user)
#     if request.method == 'POST':
#         message.is_archived = True
#         message.save()
#         messages.success(request, 'Message archived successfully.')
#     return redirect('messaging:inbox')

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
    messages = Message.objects.filter(recipients=request.user, is_archived=True).order_by('-sent_at')
    return render(request, 'messaging/archived_messages.html', {'messages': messages})

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
