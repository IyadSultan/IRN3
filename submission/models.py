# submission/models.py

from django.db import models
from django.contrib.auth.models import User
from forms_builder.models import StudyType, DynamicForm
from django.utils import timezone
from django.core.cache import cache
from django.db.utils import OperationalError
from django.apps import apps

def get_status_choices():
    DEFAULT_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        
        
    ]
    
    try:
        choices = cache.get('status_choices')
        if not choices:
            StatusChoice = apps.get_model('submission', 'StatusChoice')
            choices = list(StatusChoice.objects.filter(is_active=True).values_list('code', 'label'))
            if choices:
                cache.set('status_choices', choices)
        return choices or DEFAULT_CHOICES
    except (OperationalError, LookupError):
        return DEFAULT_CHOICES

class StatusChoice(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Status Choice'
        verbose_name_plural = 'Status Choices'

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('status_choices')

class Submission(models.Model):
    temporary_id = models.AutoField(primary_key=True)
    irb_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    title = models.CharField(max_length=255)
    primary_investigator = models.ForeignKey(
        User, related_name='primary_investigations', on_delete=models.CASCADE
    )
    study_type = models.ForeignKey(StudyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=get_status_choices,
        default='draft'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    def archive(self, user=None):
        """Archive the submission"""
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=['is_archived', 'archived_at'])

    def unarchive(self, user=None):
        """Unarchive the submission"""
        self.is_archived = False
        self.archived_at = None
        self.save(update_fields=['is_archived', 'archived_at'])

    def __str__(self):
        return f"{self.title} (ID: {self.temporary_id}, Version: {self.version})"

    def increment_version(self):
        VersionHistory.objects.create(submission=self, version=self.version, status=self.status, date=timezone.now())
        self.version += 1

    def get_required_investigator_forms(self):
        """Get all forms that require per-investigator submission."""
        return self.study_type.forms.filter(requested_per_investigator=True)

    def get_pending_investigator_forms(self, user):
        """Get forms that still need to be filled by an investigator."""
        required_forms = self.get_required_investigator_forms()
        submitted_forms = InvestigatorFormSubmission.objects.filter(
            submission=self,
            investigator=user,
            version=self.version
        ).values_list('form_id', flat=True)
        return required_forms.exclude(id__in=submitted_forms)

    def get_investigator_form_status(self):
        """Get completion status of all investigator forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return {}

        investigators = list(self.coinvestigators.all())
        investigators.append({'user': self.primary_investigator, 'role': 'Primary Investigator'})

        status = {}
        for form in required_forms:
            form_submissions = InvestigatorFormSubmission.objects.filter(
                submission=self,
                form=form,
                version=self.version
            ).select_related('investigator')

            submitted_users = {sub.investigator_id: sub.date_submitted for sub in form_submissions}
            
            # For the PI, if they submitted the submission, consider their forms complete
            if self.date_submitted and self.status == 'submitted':
                submitted_users.setdefault(
                    self.primary_investigator.id, 
                    self.date_submitted
                )

            status[form.name] = {
                'form': form,
                'investigators': [
                    {
                        'user': inv['user'] if isinstance(inv, dict) else inv.user,
                        'role': inv['role'] if isinstance(inv, dict) else 'Co-Investigator',
                        'submitted': submitted_users.get(
                            inv['user'].id if isinstance(inv, dict) else inv.user.id
                        ),
                        'is_pi': (inv['user'] if isinstance(inv, dict) else inv.user) == self.primary_investigator
                    }
                    for inv in investigators
                ]
            }
        return status

    def are_all_investigator_forms_complete(self):
        """Check if all investigators have completed their required forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return True

        investigators = list(self.coinvestigators.all().values_list('user_id', flat=True))
        # Don't include PI in check as their forms are auto-completed
        
        for form in required_forms:
            submitted_users = InvestigatorFormSubmission.objects.filter(
                submission=self,
                form=form,
                version=self.version
            ).values_list('investigator_id', flat=True)
            if not set(investigators).issubset(set(submitted_users)):
                return False
        return True
        
        

from django.db import models
from django.contrib.auth.models import User
from users.models import Role  # Add this import

class CoInvestigator(models.Model):
    submission = models.ForeignKey(
        'Submission', 
        related_name='coinvestigators',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.JSONField(default=list)  # Changed from ManyToManyField to JSONField
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['submission', 'user']
        ordering = ['order']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.submission.temporary_id}"

    def get_role_display(self):
        """Return human-readable role names"""
        role_dict = dict(COINVESTIGATOR_ROLES)
        return [role_dict.get(role, role) for role in (self.roles or [])]

from django.db import models
from django.contrib.auth.models import User

class ResearchAssistant(models.Model):
    submission = models.ForeignKey(
        'Submission',
        related_name='research_assistants',  # Add this related_name
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['submission', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.submission.temporary_id}"

class FormDataEntry(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='form_data_entries', on_delete=models.CASCADE
    )
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    date_saved = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['submission', 'form', 'field_name']),
        ]

    def __str__(self):
        return f"{self.submission} - {self.form.name} - {self.field_name}"

class Document(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='documents', on_delete=models.CASCADE
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpeg', 'jpg', 'doc', 'docx', 'txt']

    def __str__(self):
        return f"{self.file.name}"

    def filename(self):
        return self.file.name.split('/')[-1]

class VersionHistory(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='version_histories', on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField()
    status = models.CharField(
        max_length=50,
        choices=get_status_choices
    )
    date = models.DateTimeField()

    def __str__(self):
        return f"Submission {self.submission.temporary_id} - Version {self.version}"
    

from django.db import models
from django.core.cache import cache

class SystemSettings(models.Model):
    system_email = models.EmailField(
        default='aidi@khcc.jo',
        help_text='System email address used for automated messages'
    )
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def save(self, *args, **kwargs):
        cache.delete('system_settings')
        super().save(*args, **kwargs)

    @staticmethod
    def get_system_email():
        """Get the system email from settings or return default."""
        try:
            settings = SystemSettings.objects.first()
            return settings.system_email if settings else 'aidi@khcc.jo'
        except Exception:
            return 'aidi@khcc.jo'


class InvestigatorFormSubmission(models.Model):
    submission = models.ForeignKey(
        'Submission', 
        on_delete=models.CASCADE,
        related_name='investigator_form_submissions'
    )
    form = models.ForeignKey(
        'forms_builder.DynamicForm',
        on_delete=models.CASCADE
    )
    investigator = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )
    date_submitted = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()

    class Meta:
        unique_together = ['submission', 'form', 'investigator', 'version']
        ordering = ['date_submitted']

    def __str__(self):
        return f"{self.investigator.get_full_name()} - {self.form.name} (v{self.version})"