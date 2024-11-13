# Create a new file: feedback/forms.py

from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['category', 'subject', 'message', 'screenshot']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Please provide detailed feedback...'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary of your feedback'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'screenshot': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }