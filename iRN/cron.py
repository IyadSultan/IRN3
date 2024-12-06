from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models import Q, Max
from submission.models import Submission, StudyAction
from messaging.models import Message
import logging

# Set up logging
logger = logging.getLogger('IRN.security')

def get_system_user():
    """Get or create system user for notifications"""
    try:
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'aidi@khcc.jo',
                'first_name': 'AIDI',
                'last_name': 'System',
                'is_active': False
            }
        )
        return system_user
    except Exception as e:
        logger.error(f"Error getting system user: {str(e)}")
        return None

def get_last_progress_report_date(submission):
    """Get date of last progress report for a submission"""
    try:
        last_report = StudyAction.objects.filter(
            submission=submission,
            action_type='progress',
            status='completed'
        ).order_by('-date_created').first()
        
        return last_report.date_created if last_report else None
    except Exception as e:
        logger.error(f"Error getting last progress report date for submission {submission.temporary_id}: {str(e)}")
        return None

def check_progress_reports():
    """Check accepted submissions for overdue progress reports"""
    try:
        logger.info("Starting progress report check")
        
        # Get all accepted submissions
        accepted_submissions = Submission.objects.filter(
            status='accepted',
            is_archived=False
        ).select_related('primary_investigator')
        
        system_user = get_system_user()
        if not system_user:
            logger.error("System user not found, aborting progress report check")
            return
            
        current_date = timezone.now()
        
        for submission in accepted_submissions:
            try:
                # Get last progress report date or acceptance date
                last_report_date = get_last_progress_report_date(submission)
                start_date = last_report_date or submission.date_submitted
                
                if not start_date:
                    continue
                    
                weeks_elapsed = (current_date - start_date).days // 7
                
                # If it's been one year (52 weeks) or more since last report
                if weeks_elapsed >= 52:
                    # Get number of reminder weeks
                    latest_reminder = Message.objects.filter(
                        related_submission=submission,
                        subject__contains='Progress Report Reminder'
                    ).order_by('-sent_at').first()
                    
                    reminder_weeks = 0
                    if latest_reminder:
                        reminder_weeks = (current_date - latest_reminder.sent_at).days // 7
                    
                    # Send weekly reminder for first 6 weeks
                    if reminder_weeks < 6:
                        send_progress_report_reminder(submission, system_user, reminder_weeks)
                    # After 6 weeks, notify OSAR
                    elif reminder_weeks == 6:
                        notify_osar_overdue_report(submission, system_user)
                        
            except Exception as e:
                logger.error(f"Error processing submission {submission.temporary_id}: {str(e)}")
                continue
                
        logger.info("Completed progress report check")
        
    except Exception as e:
        logger.error(f"Error in check_progress_reports: {str(e)}")

def send_progress_report_reminder(submission, system_user, reminder_week):
    """Send reminder to research team about progress report"""
    try:
        # Get team members
        recipients = [submission.primary_investigator]
        recipients.extend([ci.user for ci in submission.coinvestigators.all()])
        recipients.extend([ra.user for ra in submission.research_assistants.all()])
        
        # Create the progress report URL
        progress_report_url = f"/submission/submission/{submission.temporary_id}/progress/"
        
        # Create reminder message with link
        message = Message.objects.create(
            sender=system_user,
            subject=f'Progress Report Reminder - {submission.title}',
            body=f"""
Annual progress report is due for:

Submission ID: {submission.temporary_id}
Title: {submission.title}

Please submit your progress report as soon as possible. This is reminder {reminder_week + 1} of 6.
If no response is received after 6 weeks, OSAR will be notified.

You can submit your progress report by clicking this link:
http://irn.khcc.jo{progress_report_url}

Best regards,
AIDI System
            """.strip(),
            related_submission=submission
        )
        
        # Add recipients
        for recipient in recipients:
            message.recipients.add(recipient)
            
        logger.info(f"Sent progress report reminder {reminder_week + 1} for submission {submission.temporary_id}")
        
    except Exception as e:
        logger.error(f"Error sending reminder for submission {submission.temporary_id}: {str(e)}")

def notify_osar_overdue_report(submission, system_user):
    """Notify OSAR coordinator about overdue progress report"""
    try:
        # Get OSAR coordinator
        osar_coordinator = User.objects.get(username='Bayan')
        
        message = Message.objects.create(
            sender=system_user,
            subject=f'Overdue Progress Report - {submission.title}',
            body=f"""
No progress report has been submitted after 6 weeks of reminders for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
PI: {submission.primary_investigator.get_full_name()}

The research team has been notified weekly for the past 6 weeks but no report has been submitted.
Please follow up as appropriate.

Best regards,
AIDI System
            """.strip(),
            related_submission=submission
        )
        
        message.recipients.add(osar_coordinator)
        logger.info(f"Notified OSAR about overdue report for submission {submission.temporary_id}")
        
    except User.DoesNotExist:
        logger.error(f"OSAR coordinator not found for overdue report notification - {submission.temporary_id}")
    except Exception as e:
        logger.error(f"Error notifying OSAR for submission {submission.temporary_id}: {str(e)}")