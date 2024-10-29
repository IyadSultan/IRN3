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
