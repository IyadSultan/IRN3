# submission/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Submission, Document
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
        required=True
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
        required=True
    )
    role_in_study = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Specify the role of this co-investigator in the study',
        required=True
    )
    can_submit = forms.BooleanField(required=False)
    can_edit = forms.BooleanField(required=False)
    can_view_communications = forms.BooleanField(required=False)

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