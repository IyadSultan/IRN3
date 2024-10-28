# submission/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from forms_builder.models import StudyType, DynamicForm

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('revision_requested', 'Revision Requested'),
    ('under_revision', 'Under Revision'),
    ('accepted', 'Accepted'),
    ('suspended', 'Suspended'),
    ('finished', 'Finished'),
    ('terminated', 'Terminated'),
]

class Submission(models.Model):
    temporary_id = models.AutoField(primary_key=True)
    irb_number = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=255)
    primary_investigator = models.ForeignKey(
        User, related_name='primary_investigations', on_delete=models.CASCADE
    )
    study_type = models.ForeignKey(StudyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} (ID: {self.temporary_id}, Version: {self.version})"

class CoInvestigator(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='coinvestigators', on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_in_study = models.CharField(max_length=255)
    can_submit = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role_in_study}"

class ResearchAssistant(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='research_assistants', on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_submit = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name()

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
