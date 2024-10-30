# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Document, validate_full_name
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        help_text='Enter your full name (at least three names)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password1', 'password2')

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            try:
                validate_full_name(full_name)
            except ValidationError as e:
                raise forms.ValidationError(str(e))
        return full_name

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'full_name',
            'institution',
            'mobile',
            'khcc_employee_number',
            'title',
            'role',
            'photo',
        ]
        # Exclude only the fields that shouldn't be edited by users
        exclude = ['user', 'is_approved']

class LoginForm(forms.Form):
    username_or_email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'other_document_name', 'issue_date', 'expiry_date', 'file']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        other_document_name = cleaned_data.get('other_document_name')

        if document_type == 'Other' and not other_document_name:
            raise forms.ValidationError("Please specify the document name.")

        return cleaned_data
