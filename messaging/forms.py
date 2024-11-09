from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from submission.models import Submission
from .models import Message, MessageAttachment

class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-user-field',
            'data-placeholder': 'Select recipients...'
        })
    )
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-user-field',
            'data-placeholder': 'Select CC recipients...'
        })
    )
    bcc = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-user-field',
            'data-placeholder': 'Select BCC recipients...'
        })
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    related_submission = forms.ModelChoiceField(
        queryset=Submission.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'select2',
            'data-placeholder': 'Link to a submission...'
        })
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'recipients', 'cc', 'bcc', 'related_submission']

    def clean(self):
        cleaned_data = super().clean()
        recipients = cleaned_data.get('recipients')
        
        if not recipients:
            self.add_error('recipients', 'At least one recipient is required.')
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Exclude current user from recipients
            excluded_user_queryset = User.objects.exclude(id=user.id).filter(is_active=True)
            self.fields['recipients'].queryset = excluded_user_queryset
            self.fields['cc'].queryset = excluded_user_queryset
            self.fields['bcc'].queryset = excluded_user_queryset
            
            # Update related_submission queryset
            if user.is_authenticated:
                accessible_submissions = Submission.objects.filter(
                    Q(primary_investigator=user) |
                    Q(coinvestigators__user=user) |  # Changed to access user through CoInvestigator
                    Q(research_assistants__user=user)
                ).distinct()
                self.fields['related_submission'].queryset = accessible_submissions

        for field in self.fields:
            if field not in ['recipients', 'cc', 'bcc', 'related_submission', 'attachment']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)