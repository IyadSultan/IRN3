# submission/admin.py

from django.contrib import admin
from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
    StatusChoice,
    SystemSettings,
)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('temporary_id', 'title', 'primary_investigator', 'irb_number', 'status', 'date_created', 'is_locked')
    search_fields = ('title', 'primary_investigator__username', 'irb_number')
    list_filter = ('status', 'study_type', 'is_locked')
    ordering = ('-date_created',)
    fields = ('title', 'study_type', 'primary_investigator', 'irb_number', 'status', 'date_created', 'last_modified', 'is_locked')
    readonly_fields = ('date_created', 'last_modified')

@admin.register(CoInvestigator)
class CoInvestigatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'submission', 'get_roles', 'can_edit', 'can_submit', 'can_view_communications']
    list_filter = ['can_edit', 'can_submit', 'can_view_communications']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    
    def get_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])
    get_roles.short_description = 'Roles'

@admin.register(ResearchAssistant)
class ResearchAssistantAdmin(admin.ModelAdmin):
    list_display = ('user', 'submission', 'can_submit', 'can_edit')
    list_filter = ('can_submit', 'can_edit', 'can_view_communications')
    search_fields = ('user__username', 'submission__title')

@admin.register(FormDataEntry)
class FormDataEntryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'form', 'field_name', 'date_saved', 'version')
    list_filter = ('form', 'version')
    search_fields = ('submission__title', 'field_name', 'value')
    readonly_fields = ('date_saved',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'filename', 'uploaded_by', 'uploaded_at')
    search_fields = ('submission__title', 'file', 'uploaded_by__username')
    list_filter = ('uploaded_at',)

@admin.register(VersionHistory)
class VersionHistoryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'version', 'status', 'date')
    search_fields = ('submission__title',)
    list_filter = ('status', 'date')

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(StatusChoice)
class StatusChoiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'label', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('code', 'label')
    ordering = ('order',)from django.apps import AppConfig


class SubmissionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "submission"
import os

# try to remove combined.py if it exists
if os.path.exists('combined.py'):
    os.remove('combined.py')

app_directory = "../submission/"
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/submission'

# List all HTML files in the directory
html_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

# Open the output file in append mode to avoid overwriting existing content
with open(output_file, 'a') as outfile:
    for fname in html_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)# submission/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Submission, Document
from dal import autocomplete
from django.db.models import Q

# class MessageForm(forms.ModelForm):
#     recipients = forms.ModelMultipleChoiceField(
#         queryset=User.objects.all(),
#         required=True,
#         widget=forms.SelectMultiple(attrs={'class': 'select2'})
#     )
class SubmissionForm(forms.ModelForm):
    is_primary_investigator = forms.BooleanField(
        required=False,
        initial=False,
        label='Are you the primary investigator?'
    )
    primary_investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search for investigators...'
        })
    )

    class Meta:
        model = Submission
        fields = ['title', 'study_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'study_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Set initial value for primary_investigator if user is set
            self.fields['primary_investigator'].initial = user.id
            # Keep empty queryset initially - will be populated via AJAX
            self.fields['primary_investigator'].queryset = User.objects.none()
            
        # Filter out study types that start with IRB/irb
        study_type_field = self.fields['study_type']
        study_type_field.queryset = study_type_field.queryset.exclude(
            Q(name__istartswith='irb')
        )

from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant, Submission  # Import all needed models

from django import forms
from django.contrib.auth.models import User
from users.models import Role
from .models import ResearchAssistant, CoInvestigator, Submission

class ResearchAssistantForm(forms.ModelForm):
    assistant = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Research Assistant",
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search for research assistant...'
        })
    )
    can_edit = forms.BooleanField(
        required=False, 
        label="Can Edit",
        initial=False
    )
    can_submit = forms.BooleanField(
        required=False, 
        label="Can Submit",
        initial=False
    )
    can_view_communications = forms.BooleanField(
        required=False, 
        label="Can View Communications",
        initial=False
    )

    class Meta:
        model = ResearchAssistant
        fields = ['assistant', 'can_edit', 'can_submit', 'can_view_communications']

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)

    def clean_assistant(self):
        assistant = self.cleaned_data.get('assistant')
        
        if not assistant:
            raise forms.ValidationError("Please select a research assistant.")

        if self.submission:
            # Check if user is primary investigator
            if self.submission.primary_investigator == assistant:
                raise forms.ValidationError(
                    "This user is already the primary investigator of this submission."
                )

            # Check if user is a co-investigator
            if CoInvestigator.objects.filter(submission=self.submission, user=assistant).exists():
                raise forms.ValidationError(
                    "This user is already a co-investigator of this submission."
                )

            # Check if user is already a research assistant
            if ResearchAssistant.objects.filter(submission=self.submission, user=assistant).exists():
                raise forms.ValidationError(
                    "This user is already a research assistant of this submission."
                )

        return assistant

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.cleaned_data['assistant']
        if self.submission:
            instance.submission = self.submission
        if commit:
            instance.save()
        return instance


class CoInvestigatorForm(forms.ModelForm):
    investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label="Co-Investigator",
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Search for co-investigator...'
        })
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=True,
        label="Roles",
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all applicable roles"
    )
    can_edit = forms.BooleanField(
        required=False, 
        label="Can Edit",
        initial=False
    )
    can_submit = forms.BooleanField(
        required=False, 
        label="Can Submit",
        initial=False
    )
    can_view_communications = forms.BooleanField(
        required=False, 
        label="Can View Communications",
        initial=False
    )

    class Meta:
        model = CoInvestigator
        fields = ['investigator', 'roles', 'can_edit', 'can_submit', 'can_view_communications']

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)

    def clean_investigator(self):
        investigator = self.cleaned_data.get('investigator')
        
        if not investigator:
            raise forms.ValidationError("Please select a co-investigator.")

        if self.submission:
            # Check if user is primary investigator
            if self.submission.primary_investigator == investigator:
                raise forms.ValidationError(
                    "This user is already the primary investigator of this submission."
                )

            # Check if user is a research assistant
            if ResearchAssistant.objects.filter(submission=self.submission, user=investigator).exists():
                raise forms.ValidationError(
                    "This user is already a research assistant of this submission."
                )

            # Check if user is already a co-investigator
            if CoInvestigator.objects.filter(submission=self.submission, user=investigator).exists():
                raise forms.ValidationError(
                    "This user is already a co-investigator of this submission."
                )

        return investigator

    def clean_roles(self):
        roles = self.cleaned_data.get('roles')
        if not roles:
            raise forms.ValidationError("Please select at least one role.")
        return roles

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.cleaned_data['investigator']
        if self.submission:
            instance.submission = self.submission
        if commit:
            instance.save()
            # Save the many-to-many relationships
            self.save_m2m()
        return instance

def generate_django_form(dynamic_form):
    from django import forms

    # Create a form class dynamically
    class DynamicModelForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Add any custom initialization here if needed

    # Create the form fields dictionary
    fields = {}
    for field in dynamic_form.fields.all():
        label = f"{field.displayed_name}{'*' if field.required else ''}"
        field_attrs = {
            'required': field.required,
            'label': label,
            'help_text': field.help_text,
            'initial': field.default_value,
        }
        widget_attrs = {'class': 'form-control'}

        if field.field_type == 'text':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 255,
                widget=forms.TextInput(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(
                max_length=field.max_length or 255,
                widget=forms.EmailInput(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'tel':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 15,
                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
                **field_attrs
            )
        elif field.field_type == 'textarea':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 500,
                widget=forms.Textarea(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'checkbox':
            choices = [(choice.strip(), choice.strip())
                       for choice in field.choices.split(',') if choice.strip()]
            fields[field.name] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={
                    'class': 'form-check-input'
                }),
                required=field.required
            )
        elif field.field_type == 'radio':
            choices = [(choice.strip(), choice.strip())
                       for choice in field.choices.split(',') if choice.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                **field_attrs
            )
        elif field.field_type == 'select':
            choices = [(choice.strip(), choice.strip())
                       for choice in field.choices.split(',') if choice.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=[('', '-- Select --')] + choices,
                widget=forms.Select(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'number':
            fields[field.name] = forms.IntegerField(
                widget=forms.NumberInput(attrs=widget_attrs),
                **field_attrs
            )
        elif field.field_type == 'date':
            fields[field.name] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date', **widget_attrs}),
                **field_attrs
            )
        # Add other field types as necessary

    # Add the fields to the form class
    DynamicModelForm.base_fields = fields

    return DynamicModelForm

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }# gpt_analysis.py

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
import json
from io import StringIO
import logging
import markdown2
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class ResearchAnalyzer:
    def __init__(self, submission, version):
        """Initialize the analyzer with basic settings"""
        if version is None:
            raise ValueError("Version must be specified")
            
        self.submission = submission
        self.version = version
        self.client = OpenAI()

    def get_analysis_prompt(self):
        """Generate the analysis prompt from submission data"""
        # Get form data for the current version
        form_entries = self.submission.form_data_entries.filter(version=self.version)
        
        # Build prompt from form data
        prompt = (
            """
            Please analyze the following research submission and provide detailed suggestions to enhance the project, focusing on methodology, inclusion and exclusion criteria, objectives, endpoints, statistical analysis, and any other relevant issues.

            Format your response in markdown with the following structure:

            Use # for the main title
            Use ## for section headers
            Use bold for emphasis
            Use - for bullet points
            Include sections for:
            Study Type
                Principal Investigator
                Objectives
                Methods
                Inclusion Criteria
                Exclusion Criteria
                Endpoints
                Statistical Analysis
                Other Relevant Issues
                Provide specific recommendations for improvement in each section
                End with a Summary section highlighting key suggestions and overall recommendations
                Study Information:
                """
        )
        prompt += f"Study Type: {self.submission.study_type.name}\n\n"
        
        # Group entries by form
        for form in self.submission.study_type.forms.all():
            form_data = form_entries.filter(form=form)
            if form_data:
                prompt += f"{form.name}:\n"
                for entry in form_data:
                    prompt += f"- {entry.field_name}: {entry.value}\n"
                prompt += "\n"
                
        return prompt

    def analyze_submission(self):
        """Send to GPT and get analysis"""
        cache_key = f'gpt_analysis_{self.submission.temporary_id}_{self.version}'
        cached_response = cache.get(cache_key)
        
        if cached_response:
            # Convert markdown to HTML
            html_content = markdown2.markdown(cached_response, extras=['fenced-code-blocks'])
            return mark_safe(html_content)
            
        try:
            prompt = self.get_analysis_prompt()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are KHCC Brain, an AI research advisor specializing in medical research analysis. "
                            "Provide your analysis in clear, structured markdown format. "
                            "Use proper markdown syntax and ensure the output is well-organized and professional."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            # Cache the raw markdown response
            cache.set(cache_key, analysis, 3600)
            
            # Convert markdown to HTML
            html_content = markdown2.markdown(analysis, extras=['fenced-code-blocks'])
            return mark_safe(html_content)
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return "Error in generating analysis. Please try again later."# submission/models.py

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
# submission/urls.py

from django.urls import path
from . import views

app_name = 'submission'

urlpatterns = [
    path('start-submission/<int:submission_id>/', views.start_submission, name='start_submission_with_id'),
    path('start-submission/', views.start_submission, name='start_submission'),
    path('edit-submission/<int:submission_id>/', views.edit_submission, name='edit_submission'),
    path('add-research-assistant/<int:submission_id>/', views.add_research_assistant, name='add_research_assistant'),
    path('add-coinvestigator/<int:submission_id>/', views.add_coinvestigator, name='add_coinvestigator'),
    path('submission-form/<int:submission_id>/<int:form_id>/', views.submission_form, name='submission_form'),
    path('submission-review/<int:submission_id>/', views.submission_review, name='submission_review'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-autocomplete/', views.user_autocomplete, name='user-autocomplete'),
    path('download-pdf/<int:submission_id>/', views.download_submission_pdf, name='download_submission_pdf'),
    path('download-pdf/<int:submission_id>/<int:version>/', views.download_submission_pdf, name='download_submission_pdf_version'),
    path('update-coinvestigator-order/<int:submission_id>/', views.update_coinvestigator_order, name='update_coinvestigator_order'),
    path('document-delete/<int:submission_id>/<int:document_id>/', views.document_delete, name='document_delete'),
    path('version-history/<int:submission_id>/', views.version_history, name='version_history'),
    path('compare-versions/<int:submission_id>/<int:version1>/<int:version2>/', views.compare_versions, name='compare_versions'),
    path('<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('<int:submission_id>/version/<int:version_number>/', views.view_version, name='view_version'),
    path('<int:submission_id>/compare/<int:version1_number>/<int:version2_number>/', views.compare_versions, name='compare_versions'),
]
# submission/utils.py

from users.models import UserProfile
from .models import CoInvestigator, ResearchAssistant, FormDataEntry
from forms_builder.models import DynamicForm
from django.db.models import Q
from django.utils import timezone


def has_edit_permission(user, submission):
    # Check if user is primary investigator
    if user == submission.primary_investigator:
        return True

    # Check if user is a co-investigator with edit permission
    if submission.coinvestigators.filter(user=user, can_edit=True).exists():
        return True

    # Check if user is a research assistant with edit permission
    if submission.research_assistants.filter(user=user, can_edit=True).exists():
        return True

    return False


def check_researcher_documents(submission):
    """Check documents for all researchers involved in the submission"""
    missing_documents = {}

    # Check primary investigator's documents
    pi_profile = submission.primary_investigator.userprofile
    pi_missing = []
    if pi_profile.is_gcp_expired:
        pi_missing.append('GCP Certificate (Expired or Missing)')
    if pi_profile.is_qrc_missing:
        pi_missing.append('QRC Certificate')
    if pi_profile.is_ctc_missing:
        pi_missing.append('CTC Certificate')
    if pi_profile.is_cv_missing:
        pi_missing.append('CV')
    if pi_missing:
        missing_documents['Primary Investigator'] = {
            'name': pi_profile.full_name,
            'documents': pi_missing
        }

    # Check co-investigators' documents
    for coinv in submission.coinvestigators.all():
        coinv_profile = coinv.user.userprofile
        coinv_missing = []
        if coinv_profile.is_gcp_expired:
            coinv_missing.append('GCP Certificate (Expired or Missing)')
        if coinv_profile.is_qrc_missing:
            coinv_missing.append('QRC Certificate')
        if coinv_profile.is_ctc_missing:
            coinv_missing.append('CTC Certificate')
        if coinv_profile.is_cv_missing:
            coinv_missing.append('CV')
        if coinv_missing:
            missing_documents[f'Co-Investigator: {coinv.role_in_study}'] = {
                'name': coinv_profile.full_name,
                'documents': coinv_missing
            }

    # Check research assistants' documents
    for ra in submission.research_assistants.all():
        ra_profile = ra.user.userprofile
        ra_missing = []
        if ra_profile.is_gcp_expired:
            ra_missing.append('GCP Certificate (Expired or Missing)')
        if ra_profile.is_qrc_missing:
            ra_missing.append('QRC Certificate')
        if ra_profile.is_ctc_missing:
            ra_missing.append('CTC Certificate')
        if ra_profile.is_cv_missing:
            ra_missing.append('CV')
        if ra_missing:
            missing_documents[f'Research Assistant'] = {
                'name': ra_profile.full_name,
                'documents': ra_missing
            }

    return missing_documents


def get_next_form(submission, current_form):
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index + 1] if index + 1 < len(dynamic_forms) else None
    except ValueError:
        return None


def get_previous_form(submission, current_form):
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index - 1] if index - 1 >= 0 else None
    except ValueError:
        return None

def compare_versions(submission, version1, version2):
    data_v1 = FormDataEntry.objects.filter(submission=submission, version=version1)
    data_v2 = FormDataEntry.objects.filter(submission=submission, version=version2)
    data = []
    fields = set(data_v1.values_list('field_name', flat=True)) | set(data_v2.values_list('field_name', flat=True))
    for field in fields:
        value1 = data_v1.filter(field_name=field).first()
        value2 = data_v2.filter(field_name=field).first()
        data.append({
            'field_name': field,
            'value1': value1.value if value1 else '',
            'value2': value2.value if value2 else '',
            'changed': (value1.value if value1 else '') != (value2.value if value2 else '')
        })
    return data

from django.contrib.auth.models import User
from .models import SystemSettings

def get_system_user():
    """Get or create the system user for automated messages"""
    system_email = SystemSettings.get_system_email()
    system_user, created = User.objects.get_or_create(
        username='system',
        defaults={
            'email': system_email,
            'is_active': False,  # System user can't login
            'first_name': 'AIDI',
            'last_name': 'System'
        }
    )
    # Update email if it changed in settings
    if system_user.email != system_email:
        system_user.email = system_email
        system_user.save()
    return system_userfrom django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from dal import autocomplete
import json
from io import BytesIO
from .utils import PDFGenerator, has_edit_permission, check_researcher_documents, get_next_form, get_previous_form
from .utils.pdf_generator import generate_submission_pdf
from .gpt_analysis import ResearchAnalyzer
from django.core.cache import cache

from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
)
from .forms import (
    SubmissionForm,
    ResearchAssistantForm,
    CoInvestigatorForm,
    DocumentForm,
    generate_django_form,
)
from forms_builder.models import DynamicForm
from messaging.models import Message, MessageAttachment
from users.models import SystemSettings
from django import forms
import logging

logger = logging.getLogger(__name__)

from django.db.models import Q

@login_required
def dashboard(request):
    """Display user's submissions dashboard."""
    from django.db.models import Max
    
    submissions = Submission.objects.filter(
        primary_investigator=request.user
    ).select_related(
        'primary_investigator',
        'primary_investigator__userprofile'
    )
    
    # Get the actual latest version for each submission from FormDataEntry
    for submission in submissions:
        latest_version = FormDataEntry.objects.filter(
            submission=submission
        ).values('version').aggregate(Max('version'))['version__max']
        submission.actual_version = latest_version or 1  # Use 1 if no entries found

    return render(request, 'submission/dashboard.html', {'submissions': submissions})

@login_required
def edit_submission(request, submission_id):
    """Redirect to start_submission with existing submission ID."""
    return redirect('submission:start_submission_with_id', submission_id=submission_id)

@login_required
def start_submission(request, submission_id=None):
    """Start or edit a submission."""
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        print(f"Found submission with PI: {submission.primary_investigator}")
        print(f"Current user: {request.user}")
        
        if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to edit this submission.")
            return redirect('submission:dashboard')
        
        # Only set initial data for primary_investigator, not is_primary_investigator
        initial_data = {
            'primary_investigator': submission.primary_investigator
        }
    else:
        submission = None
        initial_data = {}

    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        form = SubmissionForm(request.POST, instance=submission)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            submission = form.save(commit=False)
            # Get is_pi directly from POST data instead of cleaned_data
            is_pi = request.POST.get('is_primary_investigator') == 'on'
            
            if is_pi:
                submission.primary_investigator = request.user
            else:
                pi_user = form.cleaned_data.get('primary_investigator')
                if not pi_user:
                    messages.error(request, 'Please select a primary investigator.')
                    return render(request, 'submission/start_submission.html', {
                        'form': form,
                        'submission': submission
                    })
                submission.primary_investigator = pi_user
                
            submission.save()
            messages.success(request, f'Temporary submission ID {submission.temporary_id} generated.')
            
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
    else:
        form = SubmissionForm(instance=submission, initial=initial_data)
        # Explicitly set is_primary_investigator based on current state
        if submission and submission.primary_investigator == request.user:
            form.fields['is_primary_investigator'].initial = True
        else:
            form.fields['is_primary_investigator'].initial = False

    return render(request, 'submission/start_submission.html', {
        'form': form,
        'submission': submission,
    })

from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant  # Add this import

@login_required
def add_research_assistant(request, submission_id):
    """Add or manage research assistants for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_assistant':
            assistant_id = request.POST.get('assistant_id')
            if assistant_id:
                try:
                    assistant = ResearchAssistant.objects.get(id=assistant_id, submission=submission)
                    assistant.delete()
                    messages.success(request, 'Research assistant removed successfully.')
                except ResearchAssistant.DoesNotExist:
                    messages.error(request, 'Research assistant not found.')
            return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:start_submission_with_id', submission_id=submission.temporary_id)
            elif action == 'exit_no_save':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        form = ResearchAssistantForm(request.POST, submission=submission)
        if form.is_valid():
            assistant = form.cleaned_data.get('assistant')
            if assistant:
                ResearchAssistant.objects.create(
                    submission=submission,
                    user=assistant,
                    can_submit=form.cleaned_data.get('can_submit', False),
                    can_edit=form.cleaned_data.get('can_edit', False),
                    can_view_communications=form.cleaned_data.get('can_view_communications', False)
                )
                messages.success(request, 'Research assistant added successfully.')
                
                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please select a research assistant.')
    else:
        form = ResearchAssistantForm()

    assistants = ResearchAssistant.objects.filter(submission=submission)
    return render(request, 'submission/add_research_assistant.html', {
        'form': form,
        'submission': submission,
        'assistants': assistants
    })

@login_required
def add_coinvestigator(request, submission_id):
    """Add or manage co-investigators for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_coinvestigator':
            coinvestigator_id = request.POST.get('coinvestigator_id')
            if coinvestigator_id:
                try:
                    coinvestigator = CoInvestigator.objects.get(id=coinvestigator_id, submission=submission)
                    coinvestigator.delete()
                    messages.success(request, 'Co-investigator removed successfully.')
                except CoInvestigator.DoesNotExist:
                    messages.error(request, 'Co-investigator not found.')
            return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
            elif action == 'exit_no_save':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                first_form = submission.study_type.forms.order_by('order').first()
                if first_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id,
                                  form_id=first_form.id)
                else:
                    return redirect('submission:submission_review', 
                                  submission_id=submission.temporary_id)

        form = CoInvestigatorForm(request.POST, submission=submission)
        if form.is_valid():
            investigator = form.cleaned_data.get('investigator')
            selected_roles = form.cleaned_data.get('roles')
            
            if investigator:
                # Create the coinvestigator instance
                coinvestigator = CoInvestigator.objects.create(
                    submission=submission,
                    user=investigator,
                    can_submit=form.cleaned_data.get('can_submit', False),
                    can_edit=form.cleaned_data.get('can_edit', False),
                    can_view_communications=form.cleaned_data.get('can_view_communications', False)
                )
                
                # Add the selected roles
                if selected_roles:
                    coinvestigator.roles.set(selected_roles)
                
                messages.success(request, 'Co-investigator added successfully.')
                
                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please select a co-investigator and specify their roles.')
    else:
        form = CoInvestigatorForm()

    coinvestigators = CoInvestigator.objects.filter(submission=submission)
    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'submission': submission,
        'coinvestigators': coinvestigators
    })

@login_required
def submission_form(request, submission_id, form_id):
    """Handle dynamic form submission and display."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    dynamic_form = get_object_or_404(DynamicForm, pk=form_id)
    action = request.POST.get('action')

    def process_field_value(value, field_type):
        """Helper function to process field values based on field type."""
        if field_type == 'checkbox':
            try:
                if isinstance(value, str):
                    if value.startswith('['):
                        return json.loads(value)
                    # Handle comma-separated string values
                    return [v.strip() for v in value.split(',') if v.strip()]
                return value
            except json.JSONDecodeError:
                return []
        return value

    if request.method == 'POST':
        # Handle navigation actions without form processing
        if action in ['back', 'exit_no_save']:
            if action == 'back':
                previous_form = get_previous_form(submission, dynamic_form)
                if previous_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id, 
                                  form_id=previous_form.id)
                return redirect('submission:add_coinvestigator', 
                              submission_id=submission.temporary_id)
            return redirect('submission:dashboard')

        # Create form instance without validation
        DynamicFormClass = generate_django_form(dynamic_form)
        
        # Save all form fields without validation
        for field_name, field in DynamicFormClass.base_fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                # Handle multiple choice fields (including checkboxes)
                values = request.POST.getlist(f'form_{dynamic_form.id}-{field_name}')
                value = json.dumps(values) if values else '[]'
            else:
                value = request.POST.get(f'form_{dynamic_form.id}-{field_name}', '')
                
            FormDataEntry.objects.update_or_create(
                submission=submission,
                form=dynamic_form,
                field_name=field_name,
                version=submission.version,
                defaults={'value': value}
            )
        
        # Handle post-save navigation
        if action == 'save_exit':
            return redirect('submission:dashboard')
        elif action == 'save_continue':
            next_form = get_next_form(submission, dynamic_form)
            if next_form:
                return redirect('submission:submission_form', 
                              submission_id=submission.temporary_id, 
                              form_id=next_form.id)
            return redirect('submission:submission_review', 
                          submission_id=submission.temporary_id)
    
    # GET request handling
    DynamicFormClass = generate_django_form(dynamic_form)
    current_data = {}
    
    # Get current version's data
    for entry in FormDataEntry.objects.filter(
        submission=submission,
        form=dynamic_form,
        version=submission.version
    ):
        field = DynamicFormClass.base_fields.get(entry.field_name)
        if field:
            if isinstance(field, forms.MultipleChoiceField):
                try:
                    current_data[entry.field_name] = process_field_value(
                        entry.value, 
                        getattr(dynamic_form.fields.get(name=entry.field_name), 'field_type', None)
                    )
                except json.JSONDecodeError:
                    current_data[entry.field_name] = []
            else:
                current_data[entry.field_name] = entry.value

    # If no current data and not version 1, get previous version's data
    if not current_data and submission.version > 1 and not submission.is_locked:
        for entry in FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version - 1
        ):
            field = DynamicFormClass.base_fields.get(entry.field_name)
            if field:
                if isinstance(field, forms.MultipleChoiceField):
                    try:
                        current_data[entry.field_name] = process_field_value(
                            entry.value,
                            getattr(dynamic_form.fields.get(name=entry.field_name), 'field_type', None)
                        )
                    except json.JSONDecodeError:
                        current_data[entry.field_name] = []
                else:
                    current_data[entry.field_name] = entry.value

    # Create form instance with processed data
    form_instance = DynamicFormClass(
        initial=current_data,
        prefix=f'form_{dynamic_form.id}'
    )

    context = {
        'form': form_instance,
        'submission': submission,
        'dynamic_form': dynamic_form,
        'previous_form': get_previous_form(submission, dynamic_form),
    }
    return render(request, 'submission/dynamic_form.html', context)


@login_required
def submission_review(request, submission_id):
    """Review submission before final submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    
    if submission.is_locked and not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')

    missing_documents = check_researcher_documents(submission)
    validation_errors = {}
    
    # Validate all forms
    for dynamic_form in submission.study_type.forms.order_by('order'):
        django_form_class = generate_django_form(dynamic_form)
        entries = FormDataEntry.objects.filter(
            submission=submission, 
            form=dynamic_form, 
            version=submission.version
        )
        saved_data = {
            f'form_{dynamic_form.id}-{entry.field_name}': entry.value
            for entry in entries
        }
        
        form_instance = django_form_class(data=saved_data, prefix=f'form_{dynamic_form.id}')
        is_valid = True
        errors = {}
        
        for field_name, field in form_instance.fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                field_key = f'form_{dynamic_form.id}-{field_name}'
                field_value = saved_data.get(field_key)
                if not field_value and field.required:
                    is_valid = False
                    errors[field_name] = ['Please select at least one option']
            else:
                field_value = form_instance.data.get(f'form_{dynamic_form.id}-{field_name}')
                if field.required and not field_value:
                    is_valid = False
                    errors[field_name] = ['This field is required']

        if not is_valid:
            validation_errors[dynamic_form.name] = errors

    documents = submission.documents.all()
    doc_form = DocumentForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'analyze_submission':
            try:
                cache_key = f'gpt_analysis_{submission.temporary_id}_{submission.version}'
                analysis = cache.get(cache_key)
                
                if not analysis:
                    analyzer = ResearchAnalyzer(submission, submission.version)
                    analysis = analyzer.analyze_submission()
                    
                    if analysis and not analysis.startswith("Error"):
                        cache.set(cache_key, analysis, 3600)
                    
                context = {
                    'submission': submission,
                    'missing_documents': missing_documents,
                    'validation_errors': validation_errors,
                    'documents': documents,
                    'doc_form': doc_form,
                    'gpt_analysis': analysis
                }
                return render(request, 'submission/submission_review.html', context)
                
            except Exception as e:
                logger.error(f"Error in GPT analysis: {str(e)}")
                messages.error(request, "Error generating analysis. Please try again later.")

        elif action == 'submit_final':
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
            else:
                try:
                    with transaction.atomic():
                        # Lock submission and update status
                        submission.is_locked = True
                        submission.status = 'submitted'
                        submission.date_submitted = timezone.now()
                        submission.save()
                        
                        # Create version history entry
                        VersionHistory.objects.create(
                            submission=submission,
                            version=1,
                            status=submission.status,
                            date=timezone.now()
                        )

                        # Generate PDF
                        buffer = generate_submission_pdf(
                            submission=submission,
                            version=1,
                            user=request.user,
                            as_buffer=True
                        )

                        if not buffer:
                            raise ValueError("Failed to generate PDF for submission")

                        # Send confirmation to PI
                        pi_message = Message.objects.create(
                            sender=get_system_user(),
                            subject=f'Submission {submission.temporary_id} - Version 1 Confirmation',
                            body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

Your submission (ID: {submission.temporary_id}) has been successfully submitted.
Please find the attached PDF for your records.

Your submission will be reviewed by the OSAR who will direct it to the appropriate review bodies.

Best regards,
AIDI System
                            """.strip(),
                            study_name=submission.title,
                            related_submission=submission
                        )
                        pi_message.recipients.add(submission.primary_investigator)
                        
                        # Attach PDF to PI message
                        pdf_filename = f"submission_{submission.temporary_id}_v1.pdf"
                        attachment = MessageAttachment(message=pi_message)
                        attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                        # Notify OSAR
                        osar_coordinators = User.objects.filter(
                            groups__name='OSAR'
                        )
                        
                        osar_notification = Message.objects.create(
                            sender=get_system_user(),
                            subject=f'New Submission For Review - {submission.title}',
                            body=f"""
A new research submission requires your initial review and forwarding.

Submission Details:
- ID: {submission.temporary_id}
- Title: {submission.title}
- PI: {submission.primary_investigator.userprofile.full_name}
- Study Type: {submission.study_type.name}
- Submitted: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please review and forward this submission to the appropriate review bodies.

Access the submission here: {request.build_absolute_uri(reverse('review:review_dashboard'))}

Best regards,
AIDI System
                            """.strip(),
                            study_name=submission.title,
                            related_submission=submission
                        )
                        
                        for coordinator in osar_coordinators:
                            osar_notification.recipients.add(coordinator)

                        # Prepare for future revisions
                        submission.version = 2  # Next version will be 2
                        submission.save()

                        messages.success(request, 'Submission has been finalized and sent to OSAR.')
                        return redirect('submission:dashboard')

                except Exception as e:
                    logger.error(f"Error in submission finalization: {str(e)}")
                    logger.error("Error details:", exc_info=True)
                    messages.error(request, f"Error during submission: {str(e)}")
                    return redirect('submission:dashboard')

        elif action == 'back':
            last_form = submission.study_type.forms.order_by('-order').first()
            if last_form:
                return redirect('submission:submission_form',
                              submission_id=submission.temporary_id,
                              form_id=last_form.id)
            return redirect('submission:add_coinvestigator',
                          submission_id=submission.temporary_id)

        elif action == 'exit_no_save':
            return redirect('submission:dashboard')

        elif action == 'upload_document':
            doc_form = DocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                document = doc_form.save(commit=False)
                document.submission = submission
                document.uploaded_by = request.user
                
                ext = document.file.name.split('.')[-1].lower()
                if ext in Document.ALLOWED_EXTENSIONS:
                    document.save()
                    messages.success(request, 'Document uploaded successfully.')
                else:
                    messages.error(
                        request,
                        f'Invalid file type: .{ext}. Allowed types are: {", ".join(Document.ALLOWED_EXTENSIONS)}'
                    )
            else:
                messages.error(request, 'Please correct the errors in the document form.')

    context = {
        'submission': submission,
        'missing_documents': missing_documents,
        'validation_errors': validation_errors,
        'documents': documents,
        'doc_form': doc_form,
        'gpt_analysis': cache.get(f'gpt_analysis_{submission.temporary_id}_{submission.version}')
    }

    return render(request, 'submission/submission_review.html', context)

@login_required
def document_delete(request, submission_id, document_id):
    """Delete a document from a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    document = get_object_or_404(Document, pk=document_id, submission=submission)
    
    if request.user == document.uploaded_by or has_edit_permission(request.user, submission):
        document.file.delete()
        document.delete()
        messages.success(request, 'Document deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this document.')
    
    return redirect('submission:submission_review', submission_id=submission_id)

@login_required
def version_history(request, submission_id):
    """View version history of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    histories = submission.version_histories.order_by('-version')
    return render(request, 'submission/version_history.html', {
        'submission': submission,
        'histories': histories,
    })

@login_required
def compare_versions(request, submission_id, version1, version2):
    """Compare two versions of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    comparison_data = []
    
    for form in submission.study_type.forms.all():
        entries_v1 = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version1
        ).select_related('form')
        
        entries_v2 = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version2
        ).select_related('form')

        data_v1 = {entry.field_name: entry.value for entry in entries_v1}
        data_v2 = {entry.field_name: entry.value for entry in entries_v2}

        field_definitions = {
            field.name: field.displayed_name 
            for field in form.fields.all()
        }

        form_changes = []
        all_fields = set(data_v1.keys()) | set(data_v2.keys())
        
        for field in all_fields:
            displayed_name = field_definitions.get(field, field)
            value1 = data_v1.get(field, 'Not provided')
            value2 = data_v2.get(field, 'Not provided')

            if isinstance(value1, str) and value1.startswith('['):
                try:
                    value1 = ', '.join(json.loads(value1))
                except json.JSONDecodeError:
                    pass
            if isinstance(value2, str) and value2.startswith('['):
                try:
                    value2 = ', '.join(json.loads(value2))
                except json.JSONDecodeError:
                    pass

            if value1 != value2:
                form_changes.append({
                    'field': displayed_name,
                    'old_value': value1,
                    'new_value': value2
                })

        if form_changes:
            comparison_data.append({
                'form_name': form.name,
                'changes': form_changes
            })

    return render(request, 'submission/compare_versions.html', {
        'submission': submission,
        'version1': version1,
        'version2': version2,
        'comparison_data': comparison_data,
    })

@login_required
def download_submission_pdf(request, submission_id, version=None):
    """Generate and download PDF version of a submission."""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to view this submission.")
            return redirect('submission:dashboard')

        # If version is not specified, use version 1 for new submissions
        if version is None:
            # If submission.version is 2, it means we just submitted version 1
            version = submission.version - 1 if submission.version > 1 else 1
            
        logger.info(f"Generating PDF for submission {submission_id} version {version}")

        # Check if form entries exist for this version
        form_entries = FormDataEntry.objects.filter(
            submission=submission,
            version=version
        )
        
        if not form_entries.exists():
            logger.warning(f"No form entries found for version {version}, checking version 1")
            # Try version 1 as fallback
            version = 1
            form_entries = FormDataEntry.objects.filter(
                submission=submission,
                version=version
            )

        # Generate PDF
        response = generate_submission_pdf(
            submission=submission,
            version=version,
            user=request.user,
            as_buffer=False
        )
        
        if response is None:
            messages.error(request, "Error generating PDF. Please try again later.")
            logger.error(f"PDF generation failed for submission {submission_id} version {version}")
            return redirect('submission:dashboard')
            
        return response

    except Exception as e:
        logger.error(f"Error in download_submission_pdf: {str(e)}")
        logger.error("Error details:", exc_info=True)
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('submission:dashboard')

@login_required
def update_coinvestigator_order(request, submission_id):
    """Update the order of co-investigators in a submission."""
    if request.method == 'POST':
        submission = get_object_or_404(Submission, pk=submission_id)
        if not has_edit_permission(request.user, submission):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            order = json.loads(request.POST.get('order', '[]'))
            for index, coinvestigator_id in enumerate(order):
                CoInvestigator.objects.filter(
                    id=coinvestigator_id,
                    submission=submission
                ).update(order=index)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def user_autocomplete(request):
    term = request.GET.get('term', '').strip()
    submission_id = request.GET.get('submission_id')
    user_type = request.GET.get('user_type')  # 'investigator', 'assistant', or 'coinvestigator'
    
    if len(term) < 2:
        return JsonResponse([], safe=False)

    # Start with base user query
    users = User.objects.filter(
        Q(userprofile__full_name__icontains=term) |
        Q(first_name__icontains=term) |
        Q(last_name__icontains=term) |
        Q(email__icontains=term)
    )

    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        
        # Exclude users already assigned to this submission in any role
        excluded_users = []
        
        # Exclude primary investigator
        if submission.primary_investigator:
            excluded_users.append(submission.primary_investigator.id)
        
        # Exclude research assistants
        assistant_ids = ResearchAssistant.objects.filter(
            submission=submission
        ).values_list('user_id', flat=True)
        excluded_users.extend(assistant_ids)
        
        # Exclude co-investigators
        coinvestigator_ids = CoInvestigator.objects.filter(
            submission=submission
        ).values_list('user_id', flat=True)
        excluded_users.extend(coinvestigator_ids)

        users = users.exclude(id__in=excluded_users)

    users = users.distinct()[:10]

    results = [
        {
            'id': user.id,
            'label': f"{user.userprofile.full_name or user.get_full_name()} ({user.email})"
        }
        for user in users
    ]

    return JsonResponse(results, safe=False)

@login_required
def submission_autocomplete(request):
    """View for handling submission autocomplete requests"""
    term = request.GET.get('term', '')
    user = request.user
    
    # Query submissions that the user has access to
    submissions = Submission.objects.filter(
        Q(primary_investigator=user) |
        Q(coinvestigators__user=user) |
        Q(research_assistants__user=user),
        Q(title__icontains=term) |
        Q(irb_number__icontains=term)
    ).distinct()[:10]

    results = []
    for submission in submissions:
        label = f"{submission.title}"
        if submission.irb_number:
            label += f" (IRB: {submission.irb_number})"
        results.append({
            'id': submission.temporary_id,
            'text': label
        })

    return JsonResponse({'results': results}, safe=False)




@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    versions = submission.version_histories.all()
    return render(request, 'submission/submission_detail.html', {
        'submission': submission,
        'versions': versions
    })

@login_required
def view_version(request, submission_id, version_number):
    """View a specific version of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # Check if version exists
    version_history = get_object_or_404(
        VersionHistory, 
        submission=submission, 
        version=version_number
    )

    # Get form data for this version
    form_data = {}
    for form in submission.study_type.forms.all():
        entries = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version_number
        ).select_related('form')
        
        form_data[form.name] = {
            'form': form,
            'entries': {entry.field_name: entry.value for entry in entries}
        }

    # Get documents that existed at this version
    # You might need to adjust this depending on how you track document versions
    documents = submission.documents.filter(
        uploaded_at__lte=version_history.date
    )

    context = {
        'submission': submission,
        'version_number': version_number,
        'version_history': version_history,
        'form_data': form_data,
        'documents': documents,
        'is_current_version': version_number == submission.version,
    }
    
    return render(request, 'submission/view_version.html', context){% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Add Co-Investigator{% endblock %}

{% block page_specific_css %}
<style>
    /* Style for roles checkboxes */
    .roles-checkbox-group {
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 10px;
    }

    .role-checkbox {
        display: block;
        margin-bottom: 8px;
    }

    .role-checkbox input[type="checkbox"] {
        margin-right: 8px;
    }

    .role-checkbox label {
        font-weight: normal;
        margin-bottom: 0;
        cursor: pointer;
    }

    /* Custom scrollbar for the roles container */
    .roles-checkbox-group::-webkit-scrollbar {
        width: 8px;
    }

    .roles-checkbox-group::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .roles-checkbox-group::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    .roles-checkbox-group::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Add Co-Investigator</h2>
                    <h6 class="text-muted">Submission ID: {{ submission.temporary_id }}</h6>
                </div>
                <div class="card-body">
                    {% if coinvestigators %}
                    <div class="mb-4">
                        <h5>Current Co-Investigators:</h5>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Roles</th>
                                    <th>Permissions</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for co in coinvestigators %}
                                <tr>
                                    <td>{{ co.user.get_full_name }}</td>
                                    <td>
                                        {% for role in co.roles.all %}
                                            <span class="badge bg-secondary me-1">{{ role.name }}</span>
                                        {% endfor %}
                                    </td>
                                    <td>
                                        {% if co.can_edit %}<span class="badge bg-success">Edit</span>{% endif %}
                                        {% if co.can_submit %}<span class="badge bg-info">Submit</span>{% endif %}
                                        {% if co.can_view_communications %}<span class="badge bg-warning">View Communications</span>{% endif %}
                                    </td>
                                    <td>
                                        <form method="post" style="display: inline;">
                                            {% csrf_token %}
                                            <input type="hidden" name="coinvestigator_id" value="{{ co.id }}">
                                            <button type="submit" name="action" value="delete_coinvestigator" 
                                                    class="btn btn-danger btn-sm"
                                                    onclick="return confirm('Are you sure you want to remove this co-investigator?')">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        {# Render investigator field with crispy #}
                        {{ form.investigator|as_crispy_field }}

                        {# Custom rendering for roles field #}
                        <div class="mb-3">
                            <label class="form-label">{{ form.roles.label }}</label>
                            <div class="roles-checkbox-group">
                                {% for choice in form.roles %}
                                    <div class="role-checkbox">
                                        {{ choice.tag }}
                                        <label for="{{ choice.id_for_label }}">{{ choice.choice_label }}</label>
                                    </div>
                                {% endfor %}
                            </div>
                            {% if form.roles.errors %}
                                <div class="alert alert-danger mt-2">
                                    {{ form.roles.errors }}
                                </div>
                            {% endif %}
                            {% if form.roles.help_text %}
                                <div class="form-text text-muted">
                                    {{ form.roles.help_text }}
                                </div>
                            {% endif %}
                        </div>

                        {# Render remaining fields with crispy #}
                        {{ form.can_edit|as_crispy_field }}
                        {{ form.can_submit|as_crispy_field }}
                        {{ form.can_view_communications|as_crispy_field }}

                        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                            <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2" formnovalidate>
                                <i class="fas fa-arrow-left"></i> Back
                            </button>
                            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2" formnovalidate>
                                <i class="fas fa-times"></i> Exit without Saving
                            </button>
                            <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                                <i class="fas fa-save"></i> Save and Exit
                            </button>
                            <button type="submit" name="action" value="save_add_another" class="btn btn-info me-md-2">
                                <i class="fas fa-plus"></i> Add Co-investigator
                            </button>
                            <button type="submit" name="action" value="save_continue" class="btn btn-success">
                                <i class="fas fa-arrow-right"></i> Save and Continue
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        // Initialize investigator Select2 only
        $('#id_investigator').select2({
    theme: 'bootstrap4',
    ajax: {
        url: '{% url "submission:user-autocomplete" %}',
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return {
                term: params.term,
                submission_id: '{{ submission.id }}',
                user_type: 'coinvestigator'
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.label
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: 'Search for co-investigator...',
            allowClear: true,
            width: '100%'
        });

        // Handle initial value for investigator if exists
        {% if form.investigator.initial %}
            var initialUser = {
                id: '{{ form.investigator.initial.id }}',
                text: '{{ form.investigator.initial.get_full_name|escapejs }}'
            };
            var initialOption = new Option(initialUser.text, initialUser.id, true, true);
            $('#id_investigator').append(initialOption).trigger('change');
        {% endif %}
    });
</script>
{% endblock %}{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Add Research Assistant{% endblock %}

{% block page_specific_css %}
<style>
    /* Any additional page-specific styles */
    .badge {
        margin-right: 5px;
    }
    
    .table td {
        vertical-align: middle;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Add Research Assistant</h2>
            <h6 class="text-muted">Submission ID: {{ submission.temporary_id }}</h6>
        </div>
        <div class="card-body">
            {% if assistants %}
            <div class="mb-4">
                <h5>Current Research Assistants:</h5>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Permissions</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ra in assistants %}
                        <tr>
                            <td>{{ ra.user.get_full_name }}</td>
                            <td>
                                {% if ra.can_edit %}<span class="badge bg-success">Edit</span>{% endif %}
                                {% if ra.can_submit %}<span class="badge bg-info">Submit</span>{% endif %}
                                {% if ra.can_view_communications %}<span class="badge bg-warning">View Communications</span>{% endif %}
                            </td>
                            <td>
                                <form method="post" style="display: inline;">
                                    {% csrf_token %}
                                    <input type="hidden" name="assistant_id" value="{{ ra.id }}">
                                    <button type="submit" name="action" value="delete_assistant" 
                                            class="btn btn-danger btn-sm"
                                            onclick="return confirm('Are you sure you want to remove this research assistant?')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            <form method="post" novalidate>
                {% csrf_token %}
                {{ form|crispy }}
                <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                    <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>

                    <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                        <i class="fas fa-times"></i> Exit without Saving
                    </button>

                    <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                        <i class="fas fa-save"></i> Save and Exit
                    </button>

                    <button type="submit" name="action" value="save_add_another" class="btn btn-info me-md-2">
                        <i class="fas fa-plus"></i> Add RA
                    </button>

                    <button type="submit" name="action" value="save_continue" class="btn btn-success">
                        <i class="fas fa-arrow-right"></i> Save and Continue
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        // Initialize Select2 for assistant field
        $('#id_assistant').select2({
    theme: 'bootstrap4',
    ajax: {
        url: '{% url "submission:user-autocomplete" %}',
        dataType: 'json',
        delay: 250,
        data: function (params) {
            return {
                term: params.term,
                submission_id: '{{ submission.id }}',
                user_type: 'assistant'
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.label
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: 'Search for research assistant...',
            allowClear: true,
            width: '100%'
        });

        // Handle initial value if it exists
        {% if form.assistant.initial %}
            var initialUser = {
                id: '{{ form.assistant.initial.id }}',
                text: '{{ form.assistant.initial.get_full_name|escapejs }}'
            };
            var initialOption = new Option(initialUser.text, initialUser.id, true, true);
            $('#id_assistant').append(initialOption).trigger('change');
        {% endif %}
    });
</script>
{% endblock %}{% extends 'users/base.html' %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Version Comparison</h2>
            <h4>{{ submission.title }}</h4>
            <p>Comparing Version {{ version1 }} with Version {{ version2 }}</p>
        </div>
        <div class="card-body">
            {% if comparison_data %}
                {% for form_data in comparison_data %}
                    <h5 class="mt-4">{{ form_data.form_name }}</h5>
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Version {{ version1 }}</th>
                                <th>Version {{ version2 }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for change in form_data.changes %}
                                <tr>
                                    <td>{{ change.field }}</td>
                                    <td {% if change.old_value != change.new_value %}class="bg-light-yellow"{% endif %}>
                                        {{ change.old_value }}
                                    </td>
                                    <td {% if change.old_value != change.new_value %}class="bg-light-yellow"{% endif %}>
                                        {{ change.new_value }}
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">
                    No differences found between these versions.
                </div>
            {% endif %}

            <div class="mt-4">
                <a href="{% url 'submission:submission_review' submission.temporary_id %}" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Back to Review
                </a>
            </div>
        </div>
    </div>
</div>

<style>
    .bg-light-yellow {
        background-color: #fff3cd;
    }
</style>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">My Submissions</h1>
    <div class="mb-3">
        <a href="{% url 'submission:start_submission' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> Start New Submission
        </a>
    </div>
    <div class="table-responsive">
        <table id="submissions-table" class="table table-striped table-hover">
            <thead class="thead-light">
                <tr>
                    <th>ID</th>
                    <th>IRB Number</th>
                    <th>Title</th>
                    <th>Primary Investigator</th>
                    <th>Status</th>
                    <th>Version</th>
                    <th>Date Created</th>
                    <th>Last Modified</th>
                    <th>Actions</th>
                </tr>
            </thead>    
            <tbody>
                {% for submission in submissions %}
                <tr>
                    <td>{{ submission.temporary_id|default:"" }}</td>
                    <td>{{ submission.irb_number|default:"N/A" }}</td>
                    <td>{{ submission.title|default:"" }}</td>
                    <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                    <td>
                        <span class="badge 
                            {% if submission.status == 'draft' %}
                                badge-warning
                            {% elif submission.status == 'submitted' %}
                                badge-info
                            {% elif submission.status == 'accepted' %}
                                badge-success
                            {% elif submission.status == 'revision_requested' or submission.status == 'under_revision' %}
                                badge-primary
                            {% else %}
                                badge-secondary
                            {% endif %}">
                            {{ submission.get_status_display|default:"" }}
                        </span>
                    </td>
                    <td>{{ submission.actual_version }}</td>
                    <td data-order="{{ submission.date_created|date:'Y-m-d H:i:s' }}">
                        {{ submission.date_created|date:"M d, Y H:i"|default:"" }}
                    </td>
                    <td data-order="{{ submission.last_modified|date:'Y-m-d H:i:s' }}">
                        {{ submission.last_modified|date:"M d, Y H:i"|default:"" }}
                    </td>
                    <td>
                        {% if submission.is_locked %}
                            <a href="{% url 'submission:edit_submission' submission.temporary_id %}" 
                               class="btn btn-sm btn-danger" 
                               title="Submission Locked">
                                <i class="fas fa-lock"></i>
                            </a>
                        {% else %}
                            <a href="{% url 'submission:edit_submission' submission.temporary_id %}" 
                               class="btn btn-sm btn-success" 
                               title="Edit Submission">
                                <i class="fas fa-edit"></i>
                            </a>
                        {% endif %}
                        <a href="{% url 'submission:version_history' submission.temporary_id %}" 
                           class="btn btn-sm btn-info" 
                           title="Version History">
                            <i class="fas fa-history"></i>
                        </a>
                        <a href="{% url 'submission:download_submission_pdf' submission.temporary_id %}" 
                           class="btn btn-sm btn-secondary" 
                           title="Download PDF">
                            <i class="fas fa-file-pdf"></i>
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="9" class="text-center">No submissions found.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        $('#submissions-table').DataTable({
            "order": [[6, "desc"]],
            "columnDefs": [
                { "orderable": false, "targets": 8 }
            ]
        });
    });
</script>
{% endblock %}{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>{{ dynamic_form.name }}</h2>
            {% if submission.version > 1 and not submission.is_locked %}
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> This form has been pre-populated with data from the previous version.
            </div>
            {% endif %}
        </div>
        <div class="card-body">
            <form method="post" novalidate>
                {% csrf_token %}
                {{ form|crispy }}
                <!-- Or use {{ form.as_p }} if not using crispy_forms -->
                <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
                    {% if previous_form %}
                    <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    {% endif %}
                    <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                        <i class="fas fa-times"></i> Exit without Saving
                    </button>
                    <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                        <i class="fas fa-save"></i> Save and Exit
                    </button>
                    <button type="submit" name="action" value="save_continue" class="btn btn-success">
                        <i class="fas fa-arrow-right"></i> Save and Continue
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Edit Submission{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Edit Submission</h2>
    
    {% if messages %}
    <div class="messages">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Save Changes</button>
        <a href="{% url 'submission:dashboard' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}

{% block extra_css %}
{{ block.super }}
<style>
    .form-group label {
        font-weight: 500;
    }
    .errorlist {
        color: #dc3545;
        list-style: none;
        padding-left: 0;
        margin-bottom: 0.5rem;
    }
    select, input {
        width: 100%;
        padding: 0.375rem 0.75rem;
        font-size: 1rem;
        line-height: 1.5;
        border: 1px solid #ced4da;
        border-radius: 0.25rem;
    }
    .select2-container {
        width: 100% !important;
    }
</style>
{% endblock %}

{% block extra_js %}
{{ block.super }}
{{ form.media }}
{% endblock %}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<div class="container mt-4">
    <h1>Submission Review</h1>
    <!-- Display missing documents -->
    {% if missing_documents %}
        <div class="alert alert-danger">
            <h4>Missing Documents:</h4>
            <ul>
                {% for key, value in missing_documents.items %}
                    <li>{{ key }} - {{ value.name }}
                        <ul>
                            {% for doc in value.documents %}
                                <li>{{ doc }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <!-- Display validation errors -->
    {% if validation_errors %}
        <div class="alert alert-danger">
            <h4>Form Validation Errors:</h4>
            <ul>
                {% for form_name, errors in validation_errors.items %}
                    <li>{{ form_name }}
                        <ul>
                            {% for field, error_list in errors.items %}
                                <li>{{ field }}: {{ error_list|join:", " }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <!-- Document Repository -->
    <h2>Document Repository</h2>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ doc_form|crispy }}
        <button type="submit" name="action" value="upload_document" class="btn btn-primary">Upload Document</button>
    </form>
    <table class="table mt-3">
        <thead>
            <tr>
                <th>Filename</th>
                <th>Description</th>
                <th>Uploaded By</th>
                <th>Uploaded At</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for doc in documents %}
            <tr>
                <td>{{ doc.filename }}</td>
                <td>{{ doc.description }}</td>
                <td>{{ doc.uploaded_by.get_full_name }}</td>
                <td>{{ doc.uploaded_at }}</td>
                <td>
                    <a href="{{ doc.file.url }}" class="btn btn-sm btn-secondary">Download</a>
                    <a href="{% url 'submission:document_delete' submission.temporary_id doc.id %}" class="btn btn-sm btn-danger">Delete</a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5">No documents uploaded.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <form method="post">
        {% csrf_token %}
        <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
            <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                <i class="fas fa-arrow-left"></i> Back
            </button>
            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                <i class="fas fa-times"></i> Exit without Saving
            </button>
            <button type="submit" name="action" value="submit_final" class="btn btn-success">
                <i class="fas fa-check"></i> Submit Final
            </button>
        </div>
    </form>
</div>
{% endblock %}
{% if missing_documents %}
<div class="alert alert-warning">
    <h4 class="alert-heading">Missing or Expired Documents</h4>
    {% for role, info in missing_documents.items %}
    <div class="mb-3">
        <strong>{{ role }}: {{ info.name }}</strong>
        <ul>
            {% for doc in info.documents %}
            <li>{{ doc }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}
</div>
{% endif %} <a href="{% url 'submission:submission_review' temporary_id=submission.temporary_id %}">Review</a> {% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Start New Submission{% endblock %}

{% block page_specific_css %}
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Start New Submission</h2>
                </div>
                <div class="card-body">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        {{ form|crispy }}
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                                <i class="fas fa-times"></i> Exit without Saving
                            </button>
                            <button type="submit" name="action" value="save_exit" class="btn btn-primary me-md-2">
                                <i class="fas fa-save"></i> Save and Exit
                            </button>
                            <button type="submit" name="action" value="save_continue" class="btn btn-success">
                                <i class="fas fa-arrow-right"></i> Save and Continue
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    $(document).ready(function() {
        // Initialize Select2 for primary investigator field
        $('#id_primary_investigator').select2({
            theme: 'bootstrap4',
            ajax: {
                url: '{% url "submission:user-autocomplete" %}',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.map(function(item) {
                            return {
                                id: item.id,
                                text: item.label
                            };
                        })
                    };
                },
                cache: true
            },
            minimumInputLength: 2,
            placeholder: 'Search for investigators...',
            allowClear: true
        });

        // Handle initial value
        {% if form.primary_investigator.initial %}
        var initialUser = {
            id: {{ form.primary_investigator.initial.id }},
            text: '{{ form.primary_investigator.initial.get_full_name|escapejs }}'
        };
        var initialOption = new Option(initialUser.text, initialUser.id, true, true);
        $('#id_primary_investigator').append(initialOption).trigger('change');
        {% endif %}

        // Toggle PI field visibility
        function togglePIField() {
            if ($('#id_is_primary_investigator').is(':checked')) {
                $('#div_id_primary_investigator').hide();
            } else {
                $('#div_id_primary_investigator').show();
            }
        }

        $('#id_is_primary_investigator').change(togglePIField);
        togglePIField();
    });
</script>
{% endblock %}{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block title %}Fill Submission Forms{% endblock %}
{% block content %}
<h1>Fill Submission Forms</h1>
<form method="post" novalidate>
    {% csrf_token %}
    {% for dynamic_form, form in forms_list %}
        <h2>{{ dynamic_form.name }}</h2>
        {{ form|crispy }}
    {% endfor %}
    <button type="submit" name="action" value="save_exit" class="btn btn-primary">Save and Exit</button>
    <button type="submit" name="action" value="save_continue" class="btn btn-primary">Save and Continue</button>
    <button type="submit" name="action" value="exit_no_save" class="btn btn-secondary">Exit without Saving</button>
</form>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}My Submissions{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>My Submissions</h1>
        <a href="{% url 'submission:start_submission' %}" class="btn btn-primary">
            <i class="fas fa-plus"></i> New Submission
        </a>
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        {% endfor %}
    {% endif %}

    {% if submissions %}
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Study Type</th>
                        <th>Primary Investigator</th>
                        <th>Status</th>
                        <th>Last Updated</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for submission in submissions %}
                        <tr>
                            <td>{{ submission.title }}</td>
                            <td>{{ submission.study_type }}</td>
                            <td>{{ submission.primary_investigator.get_full_name }}</td>
                            <td>
                                <span class="badge bg-{{ submission.get_status_color }}">
                                    {{ submission.get_status_display }}
                                </span>
                            </td>
                            <td>{{ submission.updated_at|date:"M d, Y" }}</td>
                            <td>
                                <a href="{% url 'submission:edit_submission' submission_id=submission.id %}" 
                                   class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-edit"></i> Edit
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> You don't have any submissions yet. 
            <a href="{% url 'submission:start_submission' %}" class="alert-link">Create your first submission</a>.
        </div>
    {% endif %}
</div>
{% endblock %} <!DOCTYPE html>
<html>
<head>
    <title>Submission {{ submission.temporary_id }}</title>
    <style>
        /* Add styles for PDF */
    </style>
</head>
<body>
    <h1>Submission {{ submission.temporary_id }}</h1>
    <p>Title: {{ submission.title }}</p>
    <p>Primary Investigator: {{ submission.primary_investigator.get_full_name }}</p>
    <!-- Add more details as needed -->
    <h2>Form Data</h2>
    <div class="form-group">
        {% for entry in entries %}
            <h3>{{ entry.form.name }}</h3>
            <p class="form-control">{{ entry.field_name }}: {{ entry.value }}</p>
        {% endfor %}
    </div>
</body>
</html>
<!-- submission/review.html -->

{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
<div class="container mt-4">
    <h1>Submission Review</h1>

    <!-- Primary Investigator Documents Check -->
    <div class="card mb-4">
        <div class="card-header">
            <h4>Primary Investigator Documents</h4>
            <h6>{{ submission.primary_investigator.get_full_name }}</h6>
        </div>
        <div class="card-body">
            {% with profile=submission.primary_investigator.userprofile %}
            <ul class="list-group">
                <li class="list-group-item {% if profile.has_valid_gcp %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                    <i class="fas {% if profile.has_valid_gcp %}fa-check{% else %}fa-times{% endif %}"></i>
                    GCP Certificate
                    {% if profile.is_gcp_expired %}
                    <span class="badge bg-danger">Expired</span>
                    {% endif %}
                </li>
                <li class="list-group-item {% if profile.has_cv %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                    <i class="fas {% if profile.has_cv %}fa-check{% else %}fa-times{% endif %}"></i>
                    CV
                </li>
                {% if profile.role == 'KHCC investigator' %}
                <li class="list-group-item {% if profile.has_qrc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                    <i class="fas {% if profile.has_qrc %}fa-check{% else %}fa-times{% endif %}"></i>
                    QRC Certificate
                </li>
                <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                    <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                    CTC Certificate
                </li>
                {% endif %}
            </ul>
            {% endwith %}
        </div>
    </div>

    <!-- Co-Investigators Documents Check -->
    {% if submission.coinvestigator_set.exists %}
    <div class="card mb-4">
        <div class="card-header">
            <h4>Co-Investigators Documents</h4>
        </div>
        <div class="card-body">
            {% for coinv in submission.coinvestigator_set.all %}
            <div class="mb-4">
                <h6>{{ coinv.user.get_full_name }} - {{ coinv.role_in_study }}</h6>
                {% with profile=coinv.user.userprofile %}
                <ul class="list-group">
                    <li class="list-group-item {% if profile.has_valid_gcp %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_valid_gcp %}fa-check{% else %}fa-times{% endif %}"></i>
                        GCP Certificate
                        {% if profile.is_gcp_expired %}
                        <span class="badge bg-danger">Expired</span>
                        {% endif %}
                    </li>
                    <li class="list-group-item {% if profile.has_cv %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_cv %}fa-check{% else %}fa-times{% endif %}"></i>
                        CV
                    </li>
                    {% if profile.role == 'KHCC investigator' %}
                    <li class="list-group-item {% if profile.has_qrc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_qrc %}fa-check{% else %}fa-times{% endif %}"></i>
                        QRC Certificate
                    </li>
                    <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                        CTC Certificate
                    </li>
                    {% endif %}
                </ul>
                {% endwith %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Research Assistants Documents Check -->
    {% if submission.researchassistant_set.exists %}
    <div class="card mb-4">
        <div class="card-header">
            <h4>Research Assistants Documents</h4>
        </div>
        <div class="card-body">
            {% for ra in submission.researchassistant_set.all %}
            <div class="mb-4">
                <h6>{{ ra.user.get_full_name }}</h6>
                {% with profile=ra.user.userprofile %}
                <ul class="list-group">
                    <li class="list-group-item {% if profile.has_valid_gcp %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_valid_gcp %}fa-check{% else %}fa-times{% endif %}"></i>
                        GCP Certificate
                        {% if profile.is_gcp_expired %}
                        <span class="badge bg-danger">Expired</span>
                        {% endif %}
                    </li>
                    <li class="list-group-item {% if profile.has_cv %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_cv %}fa-check{% else %}fa-times{% endif %}"></i>
                        CV
                    </li>
                    {% if profile.role == 'Research Assistant/Coordinator' %}
                    <li class="list-group-item {% if profile.has_ctc %}list-group-item-success{% else %}list-group-item-danger{% endif %}">
                        <i class="fas {% if profile.has_ctc %}fa-check{% else %}fa-times{% endif %}"></i>
                        CTC Certificate
                    </li>
                    {% endif %}
                </ul>
                {% endwith %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <!-- Display missing documents -->
    {% if missing_documents %}
        <div class="alert alert-danger">
            <h4>Missing Documents:</h4>
            <ul>
                {% for key, value in missing_documents.items %}
                    <li>{{ key }} - {{ value.name }}
                        <ul>
                            {% for doc in value.documents %}
                                <li>{{ doc }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <!-- Display validation errors -->
    {% if validation_errors %}
        <div class="alert alert-danger">
            <h4>Form Validation Errors:</h4>
            <ul>
                {% for form_name, errors in validation_errors.items %}
                    <li><strong>{{ form_name }}</strong>
                        <ul>
                            {% for field, error_list in errors.items %}
                                <li>{{ field }}: {{ error_list|join:", " }}</li>
                            {% endfor %}
                        </ul>
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}

    <!-- Document Repository -->
    <h2>Document Repository</h2>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ doc_form|crispy }}
        <button type="submit" name="action" value="upload_document" class="btn btn-primary">Upload Document</button>
    </form>
    <table class="table mt-3">
        <thead>
            <tr>
                <th>Filename</th>
                <th>Description</th>
                <th>Uploaded By</th>
                <th>Uploaded At</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for doc in documents %}
            <tr>
                <td>{{ doc.file.name|slice:"documents/" }}</td>
                <td>{{ doc.description }}</td>
                <td>{{ doc.uploaded_by.get_full_name }}</td>
                <td>{{ doc.uploaded_at }}</td>
                <td>
                    <a href="{{ doc.file.url }}" class="btn btn-sm btn-secondary">Download</a>
                    <a href="{% url 'submission:document_delete' submission.temporary_id doc.id %}" class="btn btn-sm btn-danger">Delete</a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5">No documents uploaded.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- Action Buttons -->
    <form method="post">
        {% csrf_token %}
        <div class="d-grid gap-2 d-md-flex justify-content-md-start mt-4">
            <button type="submit" name="action" value="back" class="btn btn-secondary me-md-2">
                <i class="fas fa-arrow-left"></i> Back
            </button>
            <button type="submit" name="action" value="exit_no_save" class="btn btn-danger me-md-2">
                <i class="fas fa-times"></i> Exit without Saving
            </button>
            <button type="submit" name="action" value="submit_final" class="btn btn-success">
                <i class="fas fa-check"></i> Submit Final
            </button>
        </div>
    </form>

    <!-- Loading Indicator -->
    <div id="loadingIndicator" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 9999;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; text-align: center;">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 mb-0">I am thinking...</p>
        </div>
    </div>
    <p></p>
    <!-- KHCC Brain Analysis -->
    <div class="card mb-4">
        <div class="card-header">
            <h4>KHCC Brain Analysis</h4>
        </div>
        <div class="card-body">
            <form method="post" id="analysisForm">
                {% csrf_token %}
                <button type="submit" name="action" value="analyze_submission" class="btn btn-primary mb-3">
                    <i class="fas fa-brain"></i> Analyze Submission
                </button>
            </form>
            
            {% if gpt_analysis %}
            <div class="analysis-result markdown-body">
                {{ gpt_analysis|safe }}
            </div>
            {% endif %}
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const finalSubmitForm = document.querySelector('form:last-of-type');
    finalSubmitForm.addEventListener('submit', function(e) {
        if (e.target.querySelector('button[name="action"]').value === 'submit_final') {
            const hasMissingDocs = {% if missing_documents %}true{% else %}false{% endif %};
            const hasValidationErrors = {% if validation_errors %}true{% else %}false{% endif %};
            const invalidCertificates = document.querySelectorAll('.list-group-item-danger');
            const hasInvalidCertificates = invalidCertificates.length > 0;

            if (hasMissingDocs || hasValidationErrors || hasInvalidCertificates) {
                e.preventDefault();
                alert('Cannot submit: Please ensure all mandatory fields are filled and all certificates are valid.');
                return false;
            }
        }
    });

    // Loading indicator for analysis
    const analysisForm = document.getElementById('analysisForm');
    const loadingIndicator = document.getElementById('loadingIndicator');

    if (analysisForm && loadingIndicator) {
        analysisForm.addEventListener('submit', function(e) {
            console.log('Analysis form submitted');  // Debug log
            loadingIndicator.style.display = 'block';
        });
    } else {
        console.error('Analysis form or loading indicator not found');  // Debug log
    }
});
</script>

{% endblock %}{% extends 'users/base.html' %}
{% block content %}
<div class="container mt-4">
    <h1>Version History for "{{ submission.title }}"</h1>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Version</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for history in histories %}
            <tr>
                <td>{{ history.version }}</td>
                <td>{{ history.get_status_display }}</td>
                <td>{{ history.date }}</td>
                <td>
                    <a href="{% url 'submission:download_submission_pdf_version' submission.temporary_id history.version %}" class="btn btn-sm btn-secondary">Download PDF</a>
                    {% if not forloop.last %}
                    <a href="{% url 'submission:compare_versions' submission.temporary_id history.version submission.version %}" class="btn btn-sm btn-primary">Compare with Latest</a>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
