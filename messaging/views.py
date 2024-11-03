from django.shortcuts import render, get_object_or_404, redirect
from .models import Message, MessageReadStatus, Comment
from django.contrib.auth.decorators import login_required
from .forms import MessageForm, SearchForm
from django.contrib.auth.models import User
from django.db.models import Q, Count, Value
from django.db.models.functions import Concat
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

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
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.sent_at = timezone.now()
            message.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Message sent successfully.')
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
