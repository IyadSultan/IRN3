from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.text import slugify
from messaging.models import Message, MessageAttachment
from submission.utils.pdf_generator import generate_submission_pdf
from users.utils import get_system_user


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