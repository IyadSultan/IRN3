# review/forms.py

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ReviewRequest
from forms_builder.models import DynamicForm

class ReviewRequestForm(forms.ModelForm):
    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'deadline', 'message', 'selected_forms']
        widgets = {
            'deadline': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': timezone.now().date().isoformat(),
                    'class': 'form-control'
                }
            ),
            'message': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'form-control'
                }
            ),
            'selected_forms': forms.CheckboxSelectMultiple(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter reviewers to only include those in relevant groups
        self.fields['requested_to'].queryset = User.objects.filter(
            groups__name__in=['IRB Member', 'Research Council Member', 'AHARPP Reviewer']
        ).distinct().order_by('userprofile__full_name')
        
        # Get all available forms ordered by order field
        self.fields['selected_forms'].queryset = DynamicForm.objects.all().order_by('order')
        
        # Add Bootstrap classes and help text
        self.fields['requested_to'].widget.attrs['class'] = 'form-control'
        self.fields['requested_to'].help_text = 'Select the reviewer for this submission'
        self.fields['deadline'].help_text = 'Select the deadline for completing the review'
        self.fields['message'].help_text = 'Add any additional instructions or notes for the reviewer'
        self.fields['selected_forms'].help_text = 'Select the forms that need to be completed by the reviewer'

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now().date():
            raise forms.ValidationError("Deadline must be in the future")
        return deadline

    def clean(self):
        cleaned_data = super().clean()
        selected_forms = cleaned_data.get('selected_forms')
        
        if not selected_forms or len(selected_forms) == 0:
            raise forms.ValidationError("At least one form must be selected")
            
        return cleaned_data

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
