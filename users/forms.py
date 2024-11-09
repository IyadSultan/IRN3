from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import UserProfile, Document, validate_full_name
import logging

logger = logging.getLogger('IRN.users')

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator()],
        help_text='Required. Enter a valid email address.'
    )
    
    full_name = forms.CharField(
        max_length=255,
        required=True,
        help_text='Enter your full name (First and Last name)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username.lower()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already registered.")
        return email.lower()

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name:
            try:
                validate_full_name(full_name)
            except ValidationError as e:
                logger.warning(f"Full name validation failed: {str(e)}")
                raise forms.ValidationError(str(e))
        return full_name.title()  # Capitalize first letter of each word

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Split and save full name
        full_name_parts = self.cleaned_data['full_name'].split()
        user.first_name = full_name_parts[0]
        user.last_name = ' '.join(full_name_parts[1:])
        
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    mobile = forms.CharField(
        required=False,
        max_length=20,
        initial='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your mobile number (optional)'
            }
        )
    )

    class Meta:
        model = UserProfile
        fields = [
            'institution',
            'mobile',
            'khcc_employee_number',
            'title',
            'role',
            'photo',
        ]
        exclude = ['user', 'is_approved']
        
        widgets = {
            'institution': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your institution name'
                }
            ),
            'khcc_employee_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your KHCC employee number (if applicable)'
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your title'
                }
            ),
            'role': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'photo': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

        help_texts = {
            'institution': 'Your affiliated institution',
            'mobile': 'Your mobile number in international format (e.g., +962xxxxxxxxx)',
            'khcc_employee_number': 'Required for KHCC employees only',
            'title': 'Your professional title',
            'role': 'Select your role in the system',
            'photo': 'Upload a professional photo (JPEG or PNG, max 5MB)',
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile:
            return ''
        # Remove any spaces or special characters
        mobile = ''.join(filter(str.isdigit, mobile))
        if len(mobile) < 10:
            raise ValidationError("Mobile number must be at least 10 digits.")
        # Format the number with international code if not present
        if not mobile.startswith('962'):
            mobile = f'962{mobile}'
        # Format the number with + sign
        mobile = f'+{mobile}'
        return mobile

    def clean_khcc_employee_number(self):
        emp_number = self.cleaned_data.get('khcc_employee_number')
        role = self.cleaned_data.get('role')
        
        if role == 'KHCC investigator' and not emp_number:
            raise ValidationError("Employee number is required for KHCC investigators.")
            
        if emp_number:
            # Remove any spaces or special characters
            emp_number = ''.join(filter(str.isalnum, emp_number))
            if len(emp_number) < 3:
                raise ValidationError("Employee number must be at least 3 characters.")
            # Convert to uppercase# Convert to uppercase
            emp_number = emp_number.upper()
        return emp_number

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size
            if photo.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Photo size cannot exceed 5MB.")
            
            # Check file type
            file_type = photo.content_type.split('/')[-1].lower()
            if file_type not in ['jpeg', 'jpg', 'png']:
                raise ValidationError("Only JPEG and PNG images are allowed.")
            
            # Check image dimensions
            from PIL import Image
            try:
                img = Image.open(photo)
                width, height = img.size
                if width > 2000 or height > 2000:
                    raise ValidationError("Image dimensions should not exceed 2000x2000 pixels.")
                if width < 100 or height < 100:
                    raise ValidationError("Image dimensions should be at least 100x100 pixels.")
            except Exception as e:
                raise ValidationError("Invalid image file. Please upload a valid JPEG or PNG file.")
        return photo

    def clean_institution(self):
        institution = self.cleaned_data.get('institution')
        if institution:
            # Remove extra spaces and capitalize properly
            institution = ' '.join(institution.split())
            institution = institution.title()
        return institution

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            # Remove extra spaces and capitalize properly
            title = ' '.join(title.split())
            title = title.title()
        return title

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        emp_number = cleaned_data.get('khcc_employee_number')
        institution = cleaned_data.get('institution')

        # Additional role-specific validation
        if role == 'KHCC investigator':
            if institution and institution.lower() != 'king hussein cancer center':
                raise ValidationError({
                    'institution': 'KHCC investigators must be from King Hussein Cancer Center'
                })
            if not emp_number:
                raise ValidationError({
                    'khcc_employee_number': 'Employee number is required for KHCC investigators'
                })

        return cleaned_data

    def save(self, user=None, commit=True):
        profile = super().save(commit=False)
        if user:
            # Try to get existing profile or create new one
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Update the fields from the form
            profile.institution = self.cleaned_data.get('institution')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.khcc_employee_number = self.cleaned_data.get('khcc_employee_number')
            profile.title = self.cleaned_data.get('title')
            profile.role = self.cleaned_data.get('role')
            if self.cleaned_data.get('photo'):
                profile.photo = self.cleaned_data.get('photo')
            
            if commit:
                try:
                    profile.save()
                except Exception as e:
                    logger.error(f"Error saving profile: {str(e)}")
                    raise
        return profile

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username or email'
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if not username_or_email or not password:
            raise ValidationError("Both username/email and password are required.")

        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'other_document_name', 'issue_date', 'expiry_date', 'file']
        widgets = {
            'document_type': forms.Select(
                attrs={
                    'class': 'form-control',
                    'onchange': 'toggleOtherDocumentName(this.value)'
                }
            ),
            'other_document_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter the document name'
                }
            ),
            'issue_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'expiry_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'file': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

        help_texts = {
            'document_type': 'Select the type of document you are uploading',
            'other_document_name': 'If "Other" is selected, specify the document name',
            'issue_date': 'Date when the document was issued',
            'expiry_date': 'Date when the document expires (if applicable)',
            'file': 'Upload your document (PDF, DOC, DOCX, JPG, JPEG, PNG)'
        }

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get('document_type')
        other_document_name = cleaned_data.get('other_document_name')
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        file = cleaned_data.get('file')

        if document_type == 'Other' and not other_document_name:
            self.add_error('other_document_name', 
                "Please specify the document name for 'Other' document type.")

        if issue_date and expiry_date and issue_date > expiry_date:
            self.add_error('expiry_date', 
                "Expiry date cannot be earlier than issue date.")

        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                self.add_error('file', "File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_ext = f".{file.name.split('.')[-1].lower()}"
            if file_ext not in allowed_extensions:
                self.add_error('file', 
                    f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}")

        return cleaned_data

    def save(self, commit=True):
        document = super().save(commit=False)
        if commit:
            try:
                document.save()
            except Exception as e:
                logger.error(f"Error saving document: {str(e)}")
                raise
        return document
    
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class UserEditForm(forms.ModelForm):
    """Form for editing user account information"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        disabled=True,  # Username cannot be changed
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Username cannot be changed'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email.lower()

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with bootstrap styles"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'