# submission/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Submission, Document
from dal import autocomplete
from django.db.models import Q
from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant, Submission  # Import all needed models

from django import forms
from django.contrib.auth.models import User
from users.models import Role
from .models import ResearchAssistant, CoInvestigator, Submission
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
            
        # Filter out study types that start with IRB/irb or are Evaluation/Actions
        study_type_field = self.fields['study_type']
        study_type_field.queryset = study_type_field.queryset.exclude(
            Q(name__istartswith='irb') |
            Q(name__iexact='evaluation') |
            Q(name__iexact='actions')
        )



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


from iRN.constants import COINVESTIGATOR_ROLES

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
    roles = forms.MultipleChoiceField(
        choices=COINVESTIGATOR_ROLES,
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
            if self.submission.primary_investigator == investigator:
                raise forms.ValidationError(
                    "This user is already the primary investigator of this submission."
                )

            if self.submission.research_assistants.filter(user=investigator).exists():
                raise forms.ValidationError(
                    "This user is already a research assistant of this submission."
                )

            if self.submission.coinvestigators.filter(user=investigator).exists():
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
            # Save roles as a list in the JSONField
            instance.roles = list(self.cleaned_data['roles'])
            instance.save()
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
        }