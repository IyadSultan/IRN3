from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Prefetch
from django.contrib import messages
from django.template.defaulttags import register
from django.conf import settings
from .models import Message, MessageReadStatus, Comment, MessageAttachment, NotificationStatus
from .forms import MessageForm, SearchForm
from submission.models import Submission
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()

# Define default settings if not in settings.py
MAX_ATTACHMENT_SIZE = getattr(settings, 'MAX_ATTACHMENT_SIZE', 10)  # 10 MB default
ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_ATTACHMENT_EXTENSIONS', 
    ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'])

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
def compose_message(request):
    """
    Enhanced compose message view with improved handling of attachments,
    recipients, and form validation.
    """
    initial_data = {}
    
    # Handle URL parameters for pre-filled data
    recipient_id = request.GET.get('to')
    submission_id = request.GET.get('submission')
    subject = request.GET.get('subject')
    
    if recipient_id:
        try:
            recipient = User.objects.get(id=recipient_id)
            initial_data['recipients'] = [recipient]
        except User.DoesNotExist:
            messages.warning(request, "Specified recipient not found.")
    
    if submission_id:
        try:
            submission = Submission.objects.get(id=submission_id)
            initial_data['related_submission'] = submission
            if not subject:  # Auto-generate subject if none provided
                initial_data['subject'] = f"RE: {submission.title}"
        except Submission.DoesNotExist:
            messages.warning(request, "Specified submission not found.")
    
    if subject:
        initial_data['subject'] = subject

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                form.save_m2m()
                
                # Handle attachment
                if form.cleaned_data.get('attachment'):
                    MessageAttachment.objects.create(
                        message=message,
                        file=form.cleaned_data['attachment'],
                        filename=form.cleaned_data['attachment'].name
                    )
                
                messages.success(request, 'Message sent successfully.')
                return redirect('messaging:inbox')
                
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')
    else:
        form = MessageForm(user=request.user, initial=initial_data)

    context = {
        'form': form,
        'max_attachment_size': MAX_ATTACHMENT_SIZE,
        'allowed_extensions': ALLOWED_EXTENSIONS,
        'is_compose': True,  # Flag for template rendering
    }
    
    return render(request, 'messaging/compose_message.html', context)

@login_required
def reply(request, message_id):
    """
    Handle replying to a specific message.
    """
    original_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                new_message = form.save(commit=False)
                new_message.sender = request.user
                new_message.thread_id = original_message.thread_id or original_message.id
                new_message.save()
                
                # Save many-to-many relationships
                form.save_m2m()
                
                # Handle attachments
                for attachment in request.FILES.getlist('attachment'):
                    new_message.attachments.create(
                        file=attachment,
                        filename=attachment.name
                    )
                
                messages.success(request, 'Reply sent successfully.')
                return redirect('messaging:inbox')
                
            except Exception as e:
                messages.error(request, f'Error sending reply: {str(e)}')
    else:
        # Fix the reply body formatting
        reply_body = (
            "\n\n"
            f"On {original_message.sent_at.strftime('%Y-%m-%d %H:%M')}, "
            f"{original_message.sender.get_full_name()} wrote:\n"
        )
        # Add quoted message separately
        quoted_lines = [f"> {line}" for line in original_message.body.splitlines()]
        reply_body += "\n".join(quoted_lines)
        
        initial_data = {
            'subject': f"Re: {original_message.subject}" if not original_message.subject.startswith('Re: ') else original_message.subject,
            'body': reply_body,
            'recipients': [original_message.sender],
            'related_submission': original_message.related_submission
        }
        
        form = MessageForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'original_message': original_message,
        'is_reply': True,
        'max_attachment_size': 10,  # MB
        'allowed_extensions': ['.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg']
    }
    
    return render(request, 'messaging/compose_message.html', context)

@login_required
def reply_all(request, message_id):
    """
    Handle replying to all recipients of a message.
    """
    original_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                new_message = form.save(commit=False)
                new_message.sender = request.user
                new_message.thread_id = original_message.thread_id or original_message.id
                new_message.save()
                
                form.save_m2m()
                
                # Handle attachments
                for attachment in request.FILES.getlist('attachment'):
                    new_message.attachments.create(
                        file=attachment,
                        filename=attachment.name
                    )
                
                messages.success(request, 'Reply sent to all recipients.')
                return redirect('messaging:inbox')
                
            except Exception as e:
                messages.error(request, f'Error sending reply: {str(e)}')
    else:
        # Get all recipients excluding current user
        recipients = list(original_message.recipients.exclude(id=request.user.id))
        if original_message.sender != request.user:
            recipients.append(original_message.sender)
            
        # Fix the reply body formatting
        reply_body = (
            "\n\n"
            f"On {original_message.sent_at.strftime('%Y-%m-%d %H:%M')}, "
            f"{original_message.sender.get_full_name()} wrote:\n"
        )
        # Add quoted message separately
        quoted_lines = [f"> {line}" for line in original_message.body.splitlines()]
        reply_body += "\n".join(quoted_lines)
        
        initial_data = {
            'subject': f"Re: {original_message.subject}" if not original_message.subject.startswith('Re: ') else original_message.subject,
            'body': reply_body,
            'recipients': recipients,
            'cc': original_message.cc.all(),
            'related_submission': original_message.related_submission
        }
        
        form = MessageForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'original_message': original_message,
        'is_reply_all': True,
        'max_attachment_size': 10,  # MB
        'allowed_extensions': ['.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg']
    }
    
    return render(request, 'messaging/compose_message.html', context)

@login_required
def forward(request, message_id):
    """
    Handle forwarding a message to new recipients.
    """
    original_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                new_message = form.save(commit=False)
                new_message.sender = request.user
                new_message.save()
                
                form.save_m2m()
                
                # Copy original attachments
                for attachment in original_message.attachments.all():
                    new_message.attachments.create(
                        file=attachment.file,
                        filename=attachment.filename
                    )
                
                # Add new attachments
                for attachment in request.FILES.getlist('attachment'):
                    new_message.attachments.create(
                        file=attachment,
                        filename=attachment.name
                    )
                
                messages.success(request, 'Message forwarded successfully.')
                return redirect('messaging:inbox')
                
            except Exception as e:
                messages.error(request, f'Error forwarding message: {str(e)}')
    else:
        # Prepare forwarded message body
        forward_body = (
            f"\n\n"
            f"---------- Forwarded message ----------\n"
            f"From: {original_message.sender.get_full_name()}\n"
            f"Date: {original_message.sent_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Subject: {original_message.subject}\n"
            f"To: {', '.join([r.get_full_name() for r in original_message.recipients.all()])}\n\n"
            f"{original_message.body}"
        )
        
        initial_data = {
            'subject': f"Fwd: {original_message.subject}" if not original_message.subject.startswith('Fwd: ') else original_message.subject,
            'body': forward_body,
            'related_submission': original_message.related_submission
        }
        
        form = MessageForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'original_message': original_message,
        'is_forward': True,
        'max_attachment_size': 10,  # MB
        'allowed_extensions': ['.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg']
    }
    
    return render(request, 'messaging/compose_message.html', context)

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
def sent_messages(request):
    """
    View for displaying messages sent by the current user with enhanced filtering and sorting.
    """
    messages_list = Message.objects.filter(
        sender=request.user,
        is_archived=False
    ).select_related(
        'sender',
        'related_submission'
    ).prefetch_related(
        'recipients',
        'attachments'
    ).order_by('-sent_at')
    
    # Get archive success message if it exists
    archive_success = request.session.pop('archive_success', None)
    if archive_success:
        messages.success(request, archive_success)

    context = {
        'messages': messages_list,
        'is_archived': False,
        'view_type': 'sent',
        'can_archive': True,
    }
    
    return render(request, 'messaging/sent_messages.html', context)

@login_required
def archive_sent_messages(request):
    """
    Handler for archiving sent messages.
    """
    if request.method == 'POST':
        message_ids = request.POST.getlist('selected_messages[]')
        if not message_ids:
            return JsonResponse({
                'status': 'error',
                'message': 'No messages selected'
            }, status=400)
            
        try:
            messages_to_archive = Message.objects.filter(
                id__in=message_ids,
                sender=request.user
            )
            
            count = messages_to_archive.count()
            messages_to_archive.update(is_archived=True)
            
            return JsonResponse({
                'status': 'success',
                'message': f'{count} message{"s" if count != 1 else ""} archived successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

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

    results = {
        'results': [
            {
                'id': user.id,
                'text': user.get_full_name() or user.email,
                'email': user.email
            } for user in users
        ]
    }
    return JsonResponse(results)

@login_required
def submission_autocomplete(request):
    """API endpoint for submission autocomplete"""
    term = request.GET.get('term', '')
    
    submissions = Submission.objects.filter(
        Q(title__icontains=term) |
        Q(irb_number__icontains=term)
    ).distinct()[:10]
    
    results = {
        'results': [
            {
                'id': str(submission.pk),  # Use pk instead of id and convert to string
                'text': f"{submission.title} (IRB: {submission.irb_number})" if submission.irb_number else submission.title
            } for submission in submissions
        ]
    }
    return JsonResponse(results)

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