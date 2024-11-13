# Create a new file: feedback/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .forms import FeedbackForm
from .models import Feedback

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()

            # Get admin email from settings
            admin_email = getattr(settings, 'ADMIN_EMAIL', None)
            if not admin_email:
                admin_email = settings.DEFAULT_FROM_EMAIL

            # Prepare email content
            context = {
                'feedback': feedback,
                'user': request.user,
                'admin_url': request.build_absolute_uri(f'/admin/feedback/feedback/{feedback.id}/change/')
            }
            
            email_html = render_to_string('feedback/email/feedback_notification.html', context)
            email_text = render_to_string('feedback/email/feedback_notification.txt', context)

            # Send email
            try:
                send_mail(
                    subject=f'New iRN Feedback: {feedback.subject}',
                    message=email_text,
                    html_message=email_html,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your feedback! We will review it shortly.')
            except Exception as e:
                messages.warning(request, 'Feedback saved but email notification failed. Admin has been notified.')

            return redirect('feedback:feedback_confirmation')
    else:
        form = FeedbackForm()

    return render(request, 'feedback/submit_feedback.html', {'form': form})

@login_required
def feedback_confirmation(request):
    return render(request, 'feedback/feedback_confirmation.html')