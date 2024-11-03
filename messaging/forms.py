from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from submission.models import Submission
from .models import Message, MessageAttachment

class MessageForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )
    bcc = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
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
            'data-placeholder': 'Search for a submission...'
        })
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Message
        fields = ['recipients', 'cc', 'bcc', 'subject', 'body', 'related_submission']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            accessible_submissions = Submission.objects.filter(
                Q(primary_investigator=user) |
                Q(coinvestigators__user=user) |
                Q(research_assistants__user=user)
            ).distinct()
            self.fields['related_submission'].queryset = accessible_submissions

        for field in self.fields:
            if field not in ['recipients', 'cc', 'bcc', 'related_submission', 'attachment']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)
