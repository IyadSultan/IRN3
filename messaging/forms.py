# messaging/forms.py

from django import forms
from .models import Message, Comment
from django.contrib.auth.models import User
from dal import autocomplete

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipients', 'cc', 'bcc', 'subject', 'body', 'study_name', 'respond_by', 
                  'attachments', 'hashtags']
        widgets = {
            'recipients': autocomplete.ModelSelect2Multiple(url='messaging:user-autocomplete'),
            'cc': autocomplete.ModelSelect2Multiple(url='messaging:user-autocomplete'),
            'bcc': autocomplete.ModelSelect2Multiple(url='messaging:user-autocomplete'),
            'respond_by': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['body']

class SearchForm(forms.Form):
    query = forms.CharField(max_length=255)
