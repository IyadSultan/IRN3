# submission/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Submission
from dal import autocomplete

class SubmissionForm(forms.ModelForm):
    is_primary_investigator = forms.BooleanField(
        required=False, 
        initial=True, 
        label='Are you the primary investigator?'
    )
    primary_investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url='submission:user-autocomplete'),
        label='Primary Investigator'
    )

    class Meta:
        model = Submission
        fields = ['title', 'study_type', 'irb_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ResearchAssistantForm(forms.Form):
    assistant = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='submission:user-autocomplete'),
        label='Research Assistant',
        required=False  # Make field optional
    )
    can_submit = forms.BooleanField(required=False)
    can_edit = forms.BooleanField(required=False)
    can_view_communications = forms.BooleanField(required=False)

class CoInvestigatorForm(forms.Form):
    investigator = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(url='submission:user-autocomplete'),
        label='Co-Investigator',
        help_text='Select a co-investigator from the list',
        required=False  # Make field optional
    )
    role_in_study = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Specify the role of this co-investigator in the study',
        required=False  # Make field optional
    )
    can_submit = forms.BooleanField(required=False)
    can_edit = forms.BooleanField(required=False)
    can_view_communications = forms.BooleanField(required=False)

def generate_django_form(dynamic_form):
    fields = {}
    for field in dynamic_form.fields.all():
        field_kwargs = {
            'label': field.displayed_name,  # Changed from displayed_name to name
            'required': field.required,
            'help_text': field.help_text,
            'initial': field.default_value,
        }

        if field.field_type == 'text':
            fields[field.name] = forms.CharField(
                max_length=field.max_length,
                **field_kwargs
            )
        elif field.field_type == 'textarea':
            fields[field.name] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': field.rows}),
                max_length=field.max_length,
                **field_kwargs
            )
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(**field_kwargs)
        elif field.field_type == 'tel':
            fields[field.name] = forms.CharField(
                widget=forms.TextInput(attrs={'type': 'tel'}),
                **field_kwargs
            )
        elif field.field_type == 'number':
            fields[field.name] = forms.IntegerField(**field_kwargs)
        elif field.field_type == 'date':
            fields[field.name] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date'}),
                **field_kwargs
            )
        elif field.field_type == 'checkbox':
            choices = [(c.strip(), c.strip()) for c in field.choices.split(',') if c.strip()]
            fields[field.name] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                **field_kwargs
            )
        elif field.field_type == 'radio':
            choices = [(c.strip(), c.strip()) for c in field.choices.split(',') if c.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                **field_kwargs
            )
        elif field.field_type == 'select':
            choices = [(c.strip(), c.strip()) for c in field.choices.split(',') if c.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                **field_kwargs
            )

    return type('DynamicForm', (forms.Form,), fields)
