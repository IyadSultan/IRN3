# messaging/forms.py

from django import forms
from .models import Message, MessageAttachment
from django.contrib.auth.models import User
from dal import autocomplete

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipients', 'cc', 'bcc', 'subject', 'body', 'study_name', 'respond_by', 'hashtags']
        widgets = {
            'recipients': autocomplete.ModelSelect2Multiple(url='messaging:user-autocomplete'),
            'cc': autocomplete.ModelSelect2Multiple(url='messaging:user-autocomplete'),
            'bcc': autocomplete.ModelSelect2Multiple(url='messaging:user-autocomplete'),
            'respond_by': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class MessageAttachmentForm(forms.ModelForm):
    class Meta:
        model = MessageAttachment
        fields = ['file']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=255)
