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
    irb_number = models.CharField(max_length=20, blank=True, null=True)
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

    def __str__(self):
        return f"{self.title} (ID: {self.temporary_id}, Version: {self.version})"

    def increment_version(self):
        self.version += 1
        self.save()
        VersionHistory.objects.create(submission=self, version=self.version, status=self.status, date=timezone.now())

from django.db import models
from django.contrib.auth.models import User
from users.models import Role  # Add this import

class CoInvestigator(models.Model):
    submission = models.ForeignKey('Submission', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, related_name='coinvestigators')
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['submission', 'user']
        ordering = ['order']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.submission.temporary_id}"

from django.db import models
from django.contrib.auth.models import User

class ResearchAssistant(models.Model):
    submission = models.ForeignKey('Submission', on_delete=models.CASCADE)
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
        # Clear cache when settings are updated
        cache.delete('system_settings')
        super().save(*args, **kwargs)
        
    @classmethod
    def get_system_email(cls):
        # Try to get from cache first
        settings = cache.get('system_settings')
        if not settings:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
            cache.set('system_settings', settings)
        return settings.system_email
