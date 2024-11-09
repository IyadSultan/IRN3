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
