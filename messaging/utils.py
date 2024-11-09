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
        email.send()