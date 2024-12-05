# submission/models.py

from django.db import models
from django.contrib.auth.models import User
from forms_builder.models import StudyType, DynamicForm
from django.utils import timezone
from django.core.cache import cache
from django.db.utils import OperationalError
from django.apps import apps
from iRN.constants import get_submission_status_choices, COINVESTIGATOR_ROLES
import json

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
    khcc_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    title = models.CharField(max_length=255)
    primary_investigator = models.ForeignKey(
        User, related_name='primary_investigations', on_delete=models.CASCADE
    )
    study_type = models.ForeignKey(StudyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=get_submission_status_choices,
        default='draft'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    show_in_irb = models.BooleanField(default=False, help_text="Toggle visibility for IRB members")
    show_in_rc = models.BooleanField(default=False, help_text="Toggle visibility for RC members")
    # Add new field to track submitter
    submitted_by = models.ForeignKey(
        User,
        related_name='submitted_submissions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who submitted the submission"
    )

    def submit(self, submitted_by):
        self.submitted_by = submitted_by
        self.date_submitted = timezone.now()
        self.is_locked = True

                # Create version history
        VersionHistory.objects.create(
            submission=self,
            version=self.version,
            status=self.status,
            date=timezone.now()
        )
        
        # Check for required investigator forms
        required_forms = self.study_type.forms.filter(requested_per_investigator=True)
        if required_forms.exists():
            all_investigators = [self.primary_investigator]  # Include PI
            all_investigators.extend([ci.user for ci in self.coinvestigators.all()])
            
            for form in required_forms:
                for investigator in all_investigators:
                    if not InvestigatorFormSubmission.objects.filter(
                        submission=self,
                        form=form,
                        investigator=investigator,
                        version=self.version
                    ).exists():
                        self.status = 'document_missing'
                        self.save()
                        return
        
        self.status = 'submitted'
        self.save()
        


    def __str__(self):
        return f"{self.title} (ID: {self.temporary_id}, Version: {self.version})"

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

    def increment_version(self):
        """Increment submission version and create history entry."""
        VersionHistory.objects.create(
            submission=self,
            version=self.version,
            status=self.status,
            date=timezone.now()
        )
        self.version += 1

    def get_required_investigator_forms(self):
        """Get all forms that require per-investigator submission."""
        return self.study_type.forms.filter(requested_per_investigator=True)

    def get_submitters(self):
        """Get all users who have submission rights."""
        submitters = [self.primary_investigator]
        submitters.extend([ci.user for ci in self.coinvestigators.filter(can_submit=True)])
        submitters.extend([ra.user for ra in self.research_assistants.filter(can_submit=True)])
        return submitters

    def get_non_submitters(self):
        """Get all users who don't have submission rights."""
        non_submitters = []
        non_submitters.extend([ci.user for ci in self.coinvestigators.filter(can_submit=False)])
        non_submitters.extend([ra.user for ra in self.research_assistants.filter(can_submit=False)])
        return non_submitters

    def get_research_team(self):
        """Get all research assistants and co-investigators."""
        team = []
        team.extend([ci.user for ci in self.coinvestigators.all()])
        team.extend([ra.user for ra in self.research_assistants.all()])
        return team

    def has_submitted_form(self, user, form):
        """Check if a user has submitted a specific form."""
        # Direct submission check
        if InvestigatorFormSubmission.objects.filter(
            submission=self,
            form=form,
            investigator=user,
            version=self.version
        ).exists():
            return True

        # If user has submit rights and submission is submitted/pending, form is considered submitted
        if self.status in ['submitted', 'document_missing'] and user in self.get_submitters():
            return True

        return False

    def get_pending_investigator_forms(self, user):
        """Get forms that still need to be filled by an investigator."""
        if not (user == self.primary_investigator or 
                self.coinvestigators.filter(user=user).exists() or 
                self.research_assistants.filter(user=user).exists()):
            return []

        # If user has submit rights and submission is submitted/pending, no forms are pending
        if user in self.get_submitters() and self.status in ['submitted', 'document_missing']:
            return []

        required_forms = self.get_required_investigator_forms()
        submitted_forms = InvestigatorFormSubmission.objects.filter(
            submission=self,
            investigator=user,
            version=self.version
        ).values_list('form_id', flat=True)

        return list(required_forms.exclude(id__in=submitted_forms))

    def has_pending_forms(self, user):
        """Check if user has any pending forms for this submission."""
        return len(self.get_pending_investigator_forms(user)) > 0
    def get_investigator_form_status(self):
        """Get completion status of all investigator forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return {}

        # Get all team members
        submitters = self.get_submitters()
        non_submitters = self.get_non_submitters()
        all_investigators = [{'user': user, 'role': self.get_user_role(user)} 
                           for user in submitters + non_submitters]

        status = {}
        for form in required_forms:
            # Get direct form submissions
            form_submissions = InvestigatorFormSubmission.objects.filter(
                submission=self,
                form=form,
                version=self.version
            ).select_related('investigator')
            
            # Create base submission dict
            submitted_users = {sub.investigator_id: sub.date_submitted for sub in form_submissions}
            
            # For users with submit rights, mark as submitted if submission is submitted
            if self.status in ['submitted', 'document_missing'] and self.date_submitted:
                for user in submitters:
                    submitted_users.setdefault(user.id, self.date_submitted)

            status[form.name] = {
                'form': form,
                'investigators': [
                    {
                        'user': inv['user'],
                        'role': inv['role'],
                        'submitted': submitted_users.get(inv['user'].id),
                        'is_pi': inv['user'] == self.primary_investigator
                    }
                    for inv in all_investigators
                ]
            }
        return status

    def are_all_investigator_forms_complete(self):
        """Check if all investigators have completed their required forms."""
        required_forms = self.get_required_investigator_forms()
        if not required_forms.exists():
            return True

        # Get non-submitters - they always need to submit forms
        non_submitters = self.get_non_submitters()
        
        # For new submissions, include submitters in check
        if self.status not in ['submitted', 'document_missing']:
            non_submitters.extend(self.get_submitters())

        # Check each form
        for form in required_forms:
            submitted_users = [
                user.id for user in non_submitters
                if self.has_submitted_form(user, form)
            ]
            if len(submitted_users) < len(non_submitters):
                return False

        return True

    def can_user_edit(self, user):
        """Check if user can edit the submission."""
        if user == self.primary_investigator:
            return True
        return (self.coinvestigators.filter(user=user, can_edit=True).exists() or
                self.research_assistants.filter(user=user, can_edit=True).exists())

    def can_user_submit(self, user):
        """Check if user can submit the submission."""
        return user in self.get_submitters()

    def can_user_view_communications(self, user):
        """Check if user can view submission communications."""
        if user == self.primary_investigator:
            return True
        return (self.coinvestigators.filter(user=user, can_view_communications=True).exists() or
                self.research_assistants.filter(user=user, can_view_communications=True).exists())

    def get_user_role(self, user):
        """Get user's role in the submission."""
        if user == self.primary_investigator:
            return 'Primary Investigator'
        if self.coinvestigators.filter(user=user).exists():
            return 'Co-Investigator'
        if self.research_assistants.filter(user=user).exists():
            return 'Research Assistant'
        return None

    def can_user_view(self, user):
        """Determine if a user can view this submission."""
        if self.can_user_edit(user) or self.can_user_submit(user):
            return True
        if user.groups.filter(name='OSAR').exists():
            return True
        if self.show_in_irb and user.groups.filter(name='IRB').exists():
            return True
        if self.show_in_rc and user.groups.filter(name='RC').exists():
            return True
        return False

    @classmethod
    def get_visible_submissions_for_user(cls, user):
        """Get all submissions visible to a specific user."""
        if user.groups.filter(name='OSAR').exists():
            return cls.objects.all()
        
        return cls.objects.filter(
            models.Q(primary_investigator=user) |
            models.Q(coinvestigators__user=user) |
            models.Q(research_assistants__user=user) |
            models.Q(show_in_irb=True, primary_investigator__groups__name='IRB') |
            models.Q(show_in_rc=True, primary_investigator__groups__name='RC')
        ).distinct()

class CoInvestigator(models.Model):
    submission = models.ForeignKey(
        'Submission', 
        related_name='coinvestigators',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.JSONField(default=list)
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

    def log_permission_changes(self, changed_by, is_new=False):
        """Log changes to permissions."""
        if is_new:
            # Log initial permissions
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                if getattr(self, perm):
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=False,
                        new_value=True,
                        role='co_investigator',
                        notes='Initial permission setting'
                    )
            # Log initial roles
            if self.roles:
                role_names = ', '.join(self.get_role_display())
                PermissionChangeLog.objects.create(
                    submission=self.submission,
                    user=self.user,
                    changed_by=changed_by,
                    permission_type='roles',
                    old_value=False,
                    new_value=True,
                    role='co_investigator',
                    notes=f'Initial roles assigned: {role_names}'
                )
        else:
            # Get the previous state
            old_instance = CoInvestigator.objects.get(pk=self.pk)
            
            # Check for permission changes
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                old_value = getattr(old_instance, perm)
                new_value = getattr(self, perm)
                
                if old_value != new_value:
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=old_value,
                        new_value=new_value,
                        role='co_investigator'
                    )
            
            # Check for role changes
            if set(old_instance.roles) != set(self.roles):
                old_roles = ', '.join([dict(COINVESTIGATOR_ROLES).get(r, r) for r in (old_instance.roles or [])])
                new_roles = ', '.join([dict(COINVESTIGATOR_ROLES).get(r, r) for r in (self.roles or [])])
                PermissionChangeLog.objects.create(
                    submission=self.submission,
                    user=self.user,
                    changed_by=changed_by,
                    permission_type='roles',
                    old_value=False,
                    new_value=True,
                    role='co_investigator',
                    notes=f'Roles changed from: {old_roles} to: {new_roles}'
                )

class ResearchAssistant(models.Model):
    submission = models.ForeignKey(
        'Submission',
        related_name='research_assistants',
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def log_permission_changes(self, changed_by, is_new=False):
        """Log changes to permissions."""
        if is_new:
            # Log initial permissions
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                if getattr(self, perm):
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=False,
                        new_value=True,
                        role='research_assistant',
                        notes='Initial permission setting'
                    )
        else:
            # Get the previous state
            old_instance = ResearchAssistant.objects.get(pk=self.pk)
            
            # Check for permission changes
            for perm in ['can_edit', 'can_submit', 'can_view_communications']:
                old_value = getattr(old_instance, perm)
                new_value = getattr(self, perm)
                
                if old_value != new_value:
                    PermissionChangeLog.objects.create(
                        submission=self.submission,
                        user=self.user,
                        changed_by=changed_by,
                        permission_type=perm.replace('can_', ''),
                        old_value=old_value,
                        new_value=new_value,
                        role='research_assistant'
                    )

    def get_permissions_display(self):
        """Get a list of current permissions for display."""
        permissions = []
        if self.can_edit:
            permissions.append('Can Edit')
        if self.can_submit:
            permissions.append('Can Submit')
        if self.can_view_communications:
            permissions.append('Can View Communications')
        return permissions if permissions else ['No special permissions']

    def has_any_permissions(self):
        """Check if the research assistant has any permissions."""
        return any([self.can_edit, self.can_submit, self.can_view_communications])

class FormDataEntry(models.Model):
    submission = models.ForeignKey(Submission, related_name='form_data_entries', on_delete=models.CASCADE)
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    date_saved = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)
    study_action = models.ForeignKey(
        'StudyAction', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        related_name='form_data_entries'
    )

    class Meta:
        indexes = [
            models.Index(fields=['submission', 'form', 'field_name']),
        ]

    def __str__(self):
        return f"{self.submission} - {self.form.name} - {self.field_name}"

    @classmethod
    def get_version_data(cls, submission, version):
        """Get all form data for a specific version of a submission."""
        entries = cls.objects.filter(
            submission=submission,
            version=version
        ).select_related('form')

        # Group data by form
        form_data = {}
        for entry in entries:
            if entry.form_id not in form_data:
                form_data[entry.form_id] = {
                    'form': entry.form,
                    'fields': {}
                }

            # Handle JSON values
            try:
                if isinstance(entry.value, str) and entry.value.startswith('['):
                    value = ', '.join(json.loads(entry.value))
                else:
                    value = entry.value
            except (json.JSONDecodeError, TypeError):
                value = entry.value

            form_data[entry.form_id]['fields'][entry.field_name] = value

        return form_data
    
    
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
        Submission, 
        related_name='version_histories', 
        on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField()
    status = models.CharField(
        max_length=50,
        choices=get_submission_status_choices
    )
    date = models.DateTimeField()
    submitted_by = models.ForeignKey(  # New field
        User,
        related_name='version_submissions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who submitted this version"
    )

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
    

class PermissionChangeLog(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE,
        related_name='permission_changes_received'
    )
    changed_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='permission_changes_made'
    )
    permission_type = models.CharField(
        max_length=50,
        choices=[
            ('edit', 'Edit'),
            ('submit', 'Submit'),
            ('view_communications', 'View Communications')
        ]
    )
    old_value = models.BooleanField()
    new_value = models.BooleanField()
    change_date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ('co_investigator', 'Co-Investigator'),
            ('research_assistant', 'Research Assistant')
        ]
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-change_date']
        verbose_name = 'Permission Change Log'
        verbose_name_plural = 'Permission Change Logs'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.permission_type} - {self.change_date}"

    def get_change_description(self):
        """Get a human-readable description of the change."""
        action = 'granted' if self.new_value else 'removed'
        return f"{self.permission_type.title()} permission {action} for {self.user.get_full_name()} " \
               f"as {self.get_role_display()} by {self.changed_by.get_full_name()}"

class StudyAction(models.Model):
    ACTION_TYPES = [
        ('withdrawal', 'Study Withdrawal'),
        ('progress', 'Progress Report'),
        ('amendment', 'Study Amendment'),
        ('closure', 'Study Closure'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    submission = models.ForeignKey(
        'Submission', 
        on_delete=models.CASCADE,
        related_name='study_actions'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)
    version = models.IntegerField(default=1)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.submission.title}"

    def save(self, *args, **kwargs):
        if not self.version:
            self.version = self.submission.version
        super().save(*args, **kwargs)

class StudyActionDocument(models.Model):
    action = models.ForeignKey(
        StudyAction,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file = models.FileField(upload_to='study_actions/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split('/')[-1]