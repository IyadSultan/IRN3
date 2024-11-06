from messaging.models import Message

def send_review_request_notification(review_request):
    """Create notification message for new review requests."""
    subject = f'New Review Request - {review_request.submission.title}'
    
    context = {
        'review_request': review_request,
        'submission': review_request.submission,
        'reviewer': review_request.requested_to,
        'requester': review_request.requested_by,
    }
    
    message_body = f"""You have received a new review request for submission: {review_request.submission.title}
    
Requested by: {review_request.requested_by.get_full_name()}
Deadline: {review_request.deadline}

Please log in to review the submission."""

    # Create notification message
    Message.objects.create(
        sender=review_request.requested_by,
        subject=subject,
        body=message_body,
        study_name=review_request.submission.title,
        thread_id=None
    ).recipients.add(review_request.requested_to)