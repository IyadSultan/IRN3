from django import forms
from .models import Message
from django.contrib.auth.models import User
from django.db.models import Value
from django.db.models.functions import Concat

class MessageForm(forms.ModelForm):
    recipients = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'id_recipients', 'class': 'form-control', 'autocomplete': 'off'})
    )
    cc = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'id': 'id_cc', 'class': 'form-control', 'autocomplete': 'off'})
    )
    bcc = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'id': 'id_bcc', 'class': 'form-control', 'autocomplete': 'off'})
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'recipients', 'cc', 'bcc', 'study_name']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'study_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_recipients(self):
        data = self.cleaned_data['recipients']
        recipient_usernames = [item.strip() for item in data.split(',') if item.strip()]
        users = User.objects.filter(username__in=recipient_usernames)
        if not users.exists():
            raise forms.ValidationError("No matching users found for recipients.")
        return users

    def clean_cc(self):
        data = self.cleaned_data.get('cc', '')
        if data:
            cc_usernames = [item.strip() for item in data.split(',') if item.strip()]
            users = User.objects.filter(username__in=cc_usernames)
            return users
        return User.objects.none()

    def clean_bcc(self):
        data = self.cleaned_data.get('bcc', '')
        if data:
            bcc_usernames = [item.strip() for item in data.split(',') if item.strip()]
            users = User.objects.filter(username__in=bcc_usernames)
            return users
        return User.objects.none()

    def save(self, commit=True):
        message = super().save(commit=False)
        if commit:
            message.save()
            # Set the recipients, cc, bcc
            message.recipients.set(self.cleaned_data['recipients'])
            message.cc.set(self.cleaned_data.get('cc'))
            message.bcc.set(self.cleaned_data.get('bcc'))
            message.save()
        return message

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100)
