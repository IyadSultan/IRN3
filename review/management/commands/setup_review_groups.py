from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates required groups for review system'

    def handle(self, *args, **kwargs):
        required_groups = [
            'OSAR Coordinator',
            'IRB Chair',
            'RC Chair',
            'AHARRP Head'
        ]
        
        for group_name in required_groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {group_name} group')
                )
            else:
                self.stdout.write(f'{group_name} group already exists') 