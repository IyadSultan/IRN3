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
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select a reviewer...',
        }),
        label="Select Reviewer",
        help_text="Choose a qualified reviewer for this submission"
    )

    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'deadline', 'message', 'selected_forms']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, study_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get relevant reviewer groups
        reviewer_groups = set(['IRB', 'CR', 'AHARPP'])
        
        if study_type:
            reviewer_groups = set()
            try:
                if getattr(study_type, 'requires_irb', True):
                    reviewer_groups.add('IRB')
                if getattr(study_type, 'requires_research_council', True):
                    reviewer_groups.add('CR')
                if getattr(study_type, 'requires_aharpp', True):
                    reviewer_groups.add('AHARPP')
            except AttributeError:
                # If attributes don't exist, include all reviewer groups
                reviewer_groups = set(['IRB Member', 'Research Council Member', 'AHARPP Reviewer'])
        
        # Filter reviewers based on group membership
        reviewers = User.objects.filter(
            groups__name__in=reviewer_groups,
            is_active=True
        ).distinct().select_related(
            'userprofile'
        ).order_by(
            'userprofile__full_name'
        )
        
        # Update the queryset for requested_to field
        self.fields['requested_to'].queryset = reviewers
        
        # Add user full names to the display
        self.fields['requested_to'].label_from_instance = lambda user: (
            f"{user.get_full_name() or user.username} "
            f"({', '.join(user.groups.values_list('name', flat=True))})"
        )

        # Get all available forms
        form_queryset = DynamicForm.objects.all().order_by('name')
        self.fields['selected_forms'].queryset = form_queryset

        
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
