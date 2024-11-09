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
