# review/forms.py

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ReviewRequest
from forms_builder.models import DynamicForm
from dal import autocomplete

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import ReviewRequest
from forms_builder.models import DynamicForm
from dal import autocomplete

class ReviewRequestForm(forms.ModelForm):
    requested_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select a reviewer...',
        }),
        label="Select Reviewer",
        help_text="Choose a qualified reviewer for this submission"
    )

    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'deadline', 'message', 'selected_forms', 'can_forward']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'selected_forms': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'can_forward': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, study_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up reviewer field to show full name
        self.fields['requested_to'].queryset = User.objects.filter(
            is_active=True
        ).select_related('userprofile').order_by('userprofile__full_name')
        
        self.fields['requested_to'].label_from_instance = lambda user: (
            f"{user.get_full_name() or user.username}"
        )

        # Filter forms for Evaluation study type
        form_queryset = DynamicForm.objects.filter(
            study_types__name='Evaluation'
        ).order_by('order', 'name')
            
        self.fields['selected_forms'].queryset = form_queryset
        self.fields['selected_forms'].widget.attrs.update({
            'class': 'form-control',
            'size': min(10, form_queryset.count()),  # Show up to 10 items
            'multiple': 'multiple'  # Enable multiple selection
        })

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
