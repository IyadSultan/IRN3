from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.text import slugify
from messaging.models import Message, MessageAttachment
from submission.utils.pdf_generator import generate_submission_pdf
from review.utils.pdf_generator import generate_review_pdf
from users.utils import get_system_user
from django.template.loader import render_to_string


def send_review_request_notification(review_request):
    """Create notification message for new review requests."""
    submission_title = review_request.submission.title
    requester_name = review_request.requested_by.get_full_name()
    reviewer_name = review_request.requested_to.get_full_name()

    # Generate PDF of submission with the current version
    pdf_buffer = generate_submission_pdf(
        submission=review_request.submission,
        version=review_request.submission_version,  # Use the version from review request
        user=get_system_user(),  # Use system user for PDF generation
        as_buffer=True
    )

    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'New Review Request - {submission_title}',
        body=f"""
Dear {reviewer_name},

You have received a new review request.

Submission: {submission_title}
Requested by: {requester_name}
Deadline: {review_request.deadline}

Please find the submission details attached to this message. Log in to the system to submit your review.

Best regards,
iRN System
        """.strip(),
        study_name=submission_title,
        related_submission=review_request.submission
    )

    # Add recipient
    message.recipients.add(review_request.requested_to)

    # Add CC recipient
    message.cc.add(review_request.requested_by)

    if pdf_buffer:
        try:
            # Create PDF attachment
            submission_title_slug = slugify(submission_title)
            date_str = timezone.now().strftime('%Y_%m_%d')
            filename = f"submission_{submission_title_slug}_{date_str}.pdf"

            MessageAttachment.objects.create(
                message=message,
                file=ContentFile(pdf_buffer.getvalue(), name=filename),
                filename=filename
            )
        finally:
            pdf_buffer.close()

    return message


def send_review_decline_notification(review_request, decliner, reason):
    """Create notification message for declined reviews."""
    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'Review Request Declined - {review_request.submission.title}',
        body=render_to_string('review/decline_notification_email.txt', {
            'requested_by': review_request.requested_by.userprofile.full_name,
            'submission_title': review_request.submission.title,
            'decliner': decliner.userprofile.full_name,
            'reason': reason,
        }),
        study_name=review_request.submission.title,
        related_submission=review_request.submission
    )
    message.recipients.add(review_request.requested_by)
    return message


def send_extension_request_notification(review_request, new_deadline_date, reason, requester):
    """Create notification message for extension requests."""
    extension_days = (new_deadline_date - review_request.deadline).days
    
    message = Message.objects.create(
        sender=requester,
        subject=f'Extension Request for Review #{review_request.id}',
        body=f"""
Extension Request Details:
-------------------------
Review: {review_request.submission.title}
Current Deadline: {review_request.deadline}
Requested New Deadline: {new_deadline_date}
Extension Days: {extension_days} days
Reason: {reason}

Please review this request and respond accordingly.
        """.strip(),
        study_name=review_request.submission.title,
        related_submission=review_request.submission
    )
    message.recipients.add(review_request.requested_by)
    return message


def send_review_completion_notification(review, review_request, pdf_buffer):
    """Create notification message for completed reviews."""
    submission_title = review_request.submission.title
    reviewer_name = review.reviewer.get_full_name()
    
    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'Review Completed - {submission_title}',
        body=f"""
Dear {review_request.requested_by.userprofile.full_name},

A review has been completed for this submission.

Submission: {submission_title}
Reviewer: {reviewer_name}
Date Completed: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please find the detailed review report attached to this message.

Best regards,
iRN System
        """.strip(),
        study_name=submission_title,
        related_submission=review_request.submission
    )
    
    # Add recipients
    message.recipients.add(review_request.requested_by)
    message.cc.add(review_request.requested_to)
    
    if pdf_buffer:
        # Create PDF attachment
        submission_title_slug = slugify(submission_title)
        reviewer_name_slug = slugify(reviewer_name)
        date_str = timezone.now().strftime('%Y_%m_%d')
        filename = f"review_{submission_title_slug}_{reviewer_name_slug}_{date_str}.pdf"
        
        MessageAttachment.objects.create(
            message=message,
            file=ContentFile(pdf_buffer.getvalue(), name=filename),
            filename=filename
        )
    
    return message


def send_irb_decision_notification(submission, decision, comments):
    """Create notification message for IRB decisions."""
    message = Message.objects.create(
        sender=get_system_user(),
        subject=f'IRB Decision - {submission.title}',
        body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

The IRB has made a decision regarding your submission "{submission.title}".

Decision: {decision.replace('_', ' ').title()}

{comments if comments else ''}

{'Please review the comments and submit a revised version.' if decision == 'revision_required' else ''}

Best regards,
AIDI System
        """.strip(),
        study_name=submission.title,
        related_submission=submission
    )
    message.recipients.add(submission.primary_investigator)
    return message