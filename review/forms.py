# review/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import ReviewRequest
from forms_builder.forms.models import Form as DynamicForm

class ReviewRequestForm(forms.ModelForm):
    requested_to = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='IRB Member'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    selected_forms = forms.ModelMultipleChoiceField(
        queryset=DynamicForm.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'message', 'deadline', 'selected_forms']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

class ConflictOfInterestForm(forms.Form):
    conflict_of_interest = forms.ChoiceField(
        choices=[('no', 'No'), ('yes', 'Yes')],
        widget=forms.RadioSelect,
        label='Do you have a conflict of interest with this submission?'
    )
    conflict_details = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Provide details (optional)'}),
        required=False,
        label='Conflict Details'
    )
