# submission/management/commands/check_progress_reports.py

from django.core.management.base import BaseCommand
from submission.utils.progress_report_reminders import check_progress_reports

class Command(BaseCommand):
    help = 'Check submissions for overdue progress reports and send reminders'

    def handle(self, *args, **options):
        try:
            check_progress_reports()
            self.stdout.write(self.style.SUCCESS('Successfully checked progress reports'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking progress reports: {str(e)}'))