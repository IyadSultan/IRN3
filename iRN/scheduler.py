from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
import sys
from .cron import check_progress_reports

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Add the job to the scheduler
    scheduler.add_job(
        check_progress_reports,
        'interval', 
        weeks=1,  # Run weekly
        name='check_progress_reports',
        jobstore='default',
        id='check_progress_reports',
        replace_existing=True
    )
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
