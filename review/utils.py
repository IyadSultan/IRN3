# review/utils.py

from messaging.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

def send_review_request_notification(review_request):
    sender = review_request.requested_by
    recipient = review_request.requested_to
    submission = review_request.submission
    subject = f"Review Request for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    You have been requested to review the submission titled '{submission.title}' (Version {submission.version}).

    Please log in to the system to proceed with the review.

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_conflict_of_interest_notification(review_request):
    sender = review_request.requested_to  # The reviewer who declared conflict
    recipient = review_request.requested_by  # The person who requested the review
    submission = review_request.submission
    subject = f"Conflict of Interest Declared for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    The reviewer {sender.get_full_name()} has declared a conflict of interest for the submission titled '{submission.title}'.

    Please assign a new reviewer.

    Conflict Details:
    {review_request.conflict_of_interest_details or 'No additional details provided.'}

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_review_completion_notification(review_request):
    sender = review_request.requested_to  # The reviewer
    recipient = review_request.requested_by  # The person who requested the review
    submission = review_request.submission
    subject = f"Review Completed for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    The review for the submission titled '{submission.title}' has been completed by {sender.get_full_name()}.

    You can view the review by logging into the system.

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_decision_notification(submission, action, comments, decided_by):
    """Send notification about submission decision."""
    system_user = get_system_user()
    action_display = action.replace('_', ' ').title()
    
    message_content = f"""
    Your submission "{submission.title}" has been {action_display}.
    
    Decision made by: {decided_by.get_full_name() or decided_by.username}
    Comments: {comments}
    """
    
    # Get all users who need to be notified
    users_to_notify = set([submission.primary_investigator])
    users_to_notify.update(
        submission.research_assistants.filter(can_submit=True).values_list('user', flat=True)
    )
    users_to_notify.update(
        submission.coinvestigators.filter(can_submit=True).values_list('user', flat=True)
    )
    
    # Send notification to each user
    for user in users_to_notify:
        Message.objects.create(
            sender=system_user,
            body=message_content,
            subject=f"Submission {action_display} - {submission.title}",
            related_submission=submission
        ).recipients.set([user])
