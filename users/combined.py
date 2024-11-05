# users/admin.py

from django.contrib import admin
from django.contrib.auth.models import Group
from .models import UserProfile, Document, SystemSettings

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'role', 'is_approved')
    list_filter = ('is_approved', 'role')
    actions = ['approve_users']
    filter_horizontal = ('groups',)

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'issue_date', 'expiry_date')
    list_filter = ('document_type',)
    search_fields = ('user__username', 'user__email')  # Allow searching by username or email of the user

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance of settings
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib import admin
from .models import Role, UserProfile  # Add Role to your imports

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)



from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'users'

    def ready(self):
        import users.signals
# users/backends.py

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
import os

# try to remove combined.py if it exists
if os.path.exists('combined.py'):
    os.remove('combined.py')

app_directory = "../users/"
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/users'

# List all HTML files in the directory
html_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

# Open the output file in append mode to avoid overwriting existing content
with open(output_file, 'a') as outfile:
    for fname in html_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Document, validate_full_name
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        help_text='Enter your full name')
    
    class Meta:
        model = User
        fields = ('username',  'email', 'password1', 'password2')

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
            'institution',
            'mobile',
            'khcc_employee_number',
            'title',
            'role',
            'photo',
        ]
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
# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache

ROLE_CHOICES = [
    ('KHCC investigator', 'KHCC investigator'),
    ('Non-KHCC investigator', 'Non-KHCC investigator'),
    ('Research Assistant/Coordinator', 'Research Assistant/Coordinator'),
    ('OSAR head', 'OSAR head'),
    ('OSAR coordinator', 'OSAR coordinator'),
    ('IRB chair', 'IRB chair'),
    ('RC coordinator', 'RC coordinator'),
    ('IRB member', 'IRB member'),
    ('RC chair', 'RC chair'),
    ('RC member', 'RC member'),
    ('RC coordinator', 'RC coordinator'),
    ('AHARPP Head', 'AHARPP Head'),
    ('System administrator', 'System administrator'),
    ('CEO', 'CEO'),
    ('CMO', 'CMO'),
    ('AIDI Head', 'AIDI Head'),
    ('Grant Management Officer', 'Grant Management Officer'),
]

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

def validate_full_name(value):
    names = value.strip().split()
    if len(names) < 2:
        raise ValidationError('Full name must contain at least two names.')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=255, default='King Hussein Cancer Center')
    mobile = models.CharField(max_length=20)
    khcc_employee_number = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    groups = models.ManyToManyField(Group, related_name='user_profiles', blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    full_name = models.CharField(
        max_length=255,
        default='',
        help_text='Full name (at least tw names required)'
    )

    def __str__(self):
        return self.user.username

    def clean(self):
        """Validate that the full name contains at least three parts."""
        if self.full_name.strip():  # Only validate if not empty
            validate_full_name(self.full_name)

    def save(self, *args, **kwargs):
        # If full_name is not set, try to construct it from user's first and last name
        if not self.full_name and self.user:
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        super().save(*args, **kwargs)

    def is_in_group(self, group_name):
        return self.groups.filter(name=group_name).exists()
    
    def is_irb_member(self):
        return self.is_in_group('IRB Member')

    def is_research_council_member(self):
        return self.is_in_group('Research Council Member')

    def is_head_of_irb(self):
        return self.is_in_group('Head of IRB')

    def is_osar_admin(self):
        return self.is_in_group('OSAR Admin')


    @property
    def has_valid_gcp(self):
        """Check if user has a valid (non-expired) GCP certificate"""
        today = timezone.now().date()
        return self.user.documents.filter(
            document_type='GCP',
            expiry_date__gt=today
        ).exists()

    @property
    def has_qrc(self):
        """Check if user has uploaded a QRC certificate"""
        return self.user.documents.filter(
            document_type='QRC'
        ).exists()

    @property
    def has_ctc(self):
        """Check if user has uploaded a CTC certificate"""
        return self.user.documents.filter(
            document_type='CTC'
        ).exists()

    @property
    def has_cv(self):
        """Check if user has uploaded a CV"""
        return self.user.documents.filter(
            document_type='CV'
        ).exists()

    # @property
    # def is_gcp_expired(self):
    #     """Check if GCP is expired or missing"""
    #     today = timezone.now().date()
    #     latest_gcp = self.user.documents.filter(
    #         document_type='GCP'
    #     ).order_by('-expiry_date').first()
    #     if not latest_gcp or not latest_gcp.expiry_date:
    #         return True
    #     return latest_gcp.expiry_date <= today

    # # Helper properties for template usage
    # @property
    # def is_qrc_missing(self):
    #     return not self.has_qrc

    # @property
    # def is_ctc_missing(self):
    #     return not self.has_ctc

    # @property
    # def is_cv_missing(self):
    #     return not self.has_cv

class Document(models.Model):
    DOCUMENT_CHOICES = [
        ('GCP', 'Good Clinical Practice Certificate'),
        ('QRC', 'Qualitative Record Certificate'),
        ('CTC', 'Consent Training Certificate'),
        ('CV', 'Curriculum Vitae'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_CHOICES)
    other_document_name = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False  # If no expiry date, consider it not expired

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None

    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"

    @property
    def is_missing(self):
        return not self.file  # Check if the document file is missing

# users/models.py

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update the UserProfile when User is saved"""
    if created:
        # Create new profile
        UserProfile.objects.create(
            user=instance,
            full_name=f"{instance.first_name} {instance.last_name}".strip()
        )
    else:
        # Update existing profile
        if hasattr(instance, 'userprofile'):
            profile = instance.userprofile
            if not profile.full_name:
                profile.full_name = f"{instance.first_name} {instance.last_name}".strip()
            profile.save()

class SystemSettings(models.Model):
    system_email = models.EmailField(
        default='aidi@khcc.jo',
        help_text='System email address used for automated messages'
    )
    system_user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings',
        help_text='User account to be used for system messages'
    )
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def save(self, *args, **kwargs):
        cache.delete('system_settings')
        super().save(*args, **kwargs)
        
    @classmethod
    def get_system_user(cls):
        settings = cls.objects.first()
        if settings and settings.system_user:
            return settings.system_user
        # Fallback to first superuser if no system user is set
        return User.objects.filter(is_superuser=True).first()


from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username == 'system':
        UserProfile.objects.create(
            user=instance
        )
# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('upload_document/', views.upload_document, name='upload_document'),
    path('view_documents/', views.view_documents, name='view_documents'),
    path('display_document/<int:document_id>/', views.display_document, name='display_document'),
    path('profile/', views.profile, name='profile'),
    path('role-autocomplete/', views.role_autocomplete, name='role-autocomplete'),
]
from django.contrib.auth.models import User
from django.db import transaction
from .models import SystemSettings

def get_system_user():
    """Get or create the system user for automated messages"""
    with transaction.atomic():
        system_email = SystemSettings.get_system_email()
        
        # Try to get existing system user
        try:
            system_user = User.objects.select_related('userprofile').get(username='system')
            # Update email if it changed in settings
            if system_user.email != system_email:
                system_user.email = system_email
                system_user.save()
        except User.DoesNotExist:
            # Create new system user if it doesn't exist
            system_user = User.objects.create(
                username='system',
                email=system_email,
                is_active=False,
                first_name='AIDI',
                last_name='System'
            )

        return system_user# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm, DocumentForm, UserProfileForm
from django.contrib import messages
from datetime import date
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import os
from django.db import transaction
from .models import UserProfile, Role  # Add Role to the imports

@login_required
def profile(request):
    today = date.today()
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('users:profile')
        else:
            print(profile_form.errors)
    else:
        profile_form = UserProfileForm(instance=request.user.userprofile)

    # Prepare documents with pre-calculated expiry information
    documents = []
    for doc in request.user.documents.all():
        doc_info = {
            'document': doc,
            'days_until_expiry': (doc.expiry_date - today).days if doc.expiry_date else None,
            'is_expiring_soon': doc.expiry_date and (doc.expiry_date - today).days < 30 if doc.expiry_date else False
        }
        documents.append(doc_info)

    context = {
        'profile_form': profile_form,
        'today': today,
        'documents': documents,
    }
    return render(request, 'users/profile.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    full_name_parts = user_form.cleaned_data['full_name'].split()
                    user.first_name = full_name_parts[0]
                    user.last_name = ' '.join(full_name_parts[1:])
                    user.save()
                    
                    profile = user.userprofile
                    profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
                    if profile_form.is_valid():
                        profile_form.save()
                    
                    messages.success(request, 'Registration successful. Awaiting approval from administrator.')
                    return redirect('users:login')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'usage_agreement': 'By registering, you agree to the terms and conditions of use.',
    }
    return render(request, 'users/register.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('messaging:inbox')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please provide both username and password')
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('users:login')

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('users:view_documents')
    else:
        form = DocumentForm()
    return render(request, 'users/upload_document.html', {'form': form})

@login_required
def view_documents(request):
    documents = request.user.documents.all()
    documents_with_expiry = []
    
    for document in documents:
        doc_info = {
            'document': document,
            'days_until_expiry': None,
            'file_extension': os.path.splitext(document.file.name)[1].lower()
        }
        
        if document.expiry_date:
            doc_info['days_until_expiry'] = (document.expiry_date - date.today()).days
            
        documents_with_expiry.append(doc_info)
    
    context = {'documents': documents_with_expiry}
    return render(request, 'users/view_documents.html', context)

@login_required
def display_document(request, document_id):
    document = request.user.documents.get(id=document_id)
    file_path = document.file.path
    file_extension = os.path.splitext(document.file.name)[1].lower()
    
    if file_extension == '.pdf':
        try:
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            messages.error(request, f"Document with ID {document_id} not found.")
            return HttpResponseRedirect(reverse("users:view_documents"))
    else:
        return FileResponse(open(file_path, 'rb'))

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Role  # Add this import

@login_required
def role_autocomplete(request):
    term = request.GET.get('term', '').strip()
    
    if len(term) < 2:
        return JsonResponse([], safe=False)

    roles = Role.objects.filter(
        name__icontains=term
    )[:10]

    results = [
        {
            'id': role.id,
            'label': role.name
        }
        for role in roles
    ]

    return JsonResponse(results, safe=False)








# This file should be empty

default_app_config = 'users.apps.UsersConfig'
<!DOCTYPE html>
<html lang="en">
<head>
    {% load static %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}iRN System{% endblock %}</title>

    <!-- CSS Dependencies -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css" rel="stylesheet" />
    <link href="https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css" rel="stylesheet" />
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.24/css/dataTables.bootstrap4.min.css">
    <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

    <style>
        :root {
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --background-color: #ecf0f1;
            --text-color: #34495e;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
        }

        .navbar {
            background-color: var(--primary-color);
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }

        .navbar-brand, .navbar-nav .nav-link {
            color: white !important;
        }

        .sidebar {
            background-color: white;
            box-shadow: 2px 0 5px rgba(0,0,0,.1);
            height: calc(100vh - 56px);
            position: fixed;
            top: 56px;
            left: 0;
            width: 250px;
            padding-top: 20px;
        }

        .sidebar .nav-link {
            color: var(--secondary-color);
            padding: 10px 20px;
            border-left: 3px solid transparent;
        }

        .sidebar .nav-link:hover, .sidebar .nav-link.active {
            background-color: rgba(52, 152, 219, 0.1);
            border-left-color: var(--primary-color);
        }

        .main-content {
            margin-left: 250px;
            padding: 20px;
        }

        .card {
            box-shadow: 0 4px 6px rgba(0,0,0,.1);
            border: none;
            border-radius: 8px;
        }

        /* Select2 Styles */
        .select2-container {
            width: 100% !important;
            margin-bottom: 10px;
        }
        
        .select2-selection--single {
            height: 38px !important;
            padding: 5px !important;
            border: 1px solid #ced4da !important;
            border-radius: 4px !important;
        }
        
        .select2-selection__rendered {
            line-height: 26px !important;
            padding-left: 8px !important;
        }
        
        .select2-selection__arrow {
            height: 36px !important;
        }
        
        .select2-selection--multiple {
            border: 1px solid #ced4da !important;
            min-height: 38px !important;
        }
        
        .select2-search__field {
            margin-top: 5px !important;
        }
        
        .select2-container .select2-selection--single .select2-selection__clear {
            margin-right: 25px;
            color: #999;
            font-size: 18px;
        }

        /* DataTables Custom Styles */
        .dataTables_wrapper .dataTables_length select {
            min-width: 60px;
            padding: 4px;
        }

        .dataTables_wrapper .dataTables_filter input {
            margin-left: 5px;
            padding: 4px;
        }

        .dataTables_wrapper .dataTables_paginate .paginate_button {
            padding: 0.3em 0.8em;
            margin: 0 2px;
        }

        .dataTables_wrapper .dataTables_info {
            padding-top: 10px;
        }

        /* Badge and Button Styles */
        .badge {
            padding: 0.4em 0.8em;
            font-size: 0.85em;
        }

        .badge-warning { background-color: #ffc107; color: #000; }
        .badge-info { background-color: #17a2b8; color: #fff; }
        .badge-success { background-color: #28a745; color: #fff; }
        .badge-primary { background-color: #007bff; color: #fff; }
        .badge-secondary { background-color: #6c757d; color: #fff; }

        .btn-sm {
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
            line-height: 1.5;
            border-radius: 0.2rem;
        }

        /* Dropdown Styles */
        .dropdown-toggle::after {
            display: inline-block;
            margin-left: 0.255em;
            vertical-align: 0.255em;
            content: "";
            border-top: 0.3em solid;
            border-right: 0.3em solid transparent;
            border-bottom: 0;
            border-left: 0.3em solid transparent;
        }

        .dropdown-menu { margin-top: 0; }
        
        .dropdown-item:hover {
            background-color: rgba(52, 152, 219, 0.1);
        }
        
        .dropdown-item.text-danger:hover {
            background-color: rgba(220, 53, 69, 0.1);
        }

        /* Popup Styles */
        .custom-popup {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            min-width: 300px;
            max-width: 80%;
        }

        .popup-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }

        .popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }

        .popup-close {
            cursor: pointer;
            font-size: 20px;
            color: #666;
        }

        .popup-content {
            margin-bottom: 15px;
        }

        .popup-footer {
            text-align: right;
        }

        .popup-button {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .popup-button:hover {
            background: #0056b3;
        }

        /* Message Styles */
        .message-error {
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
        }

        .message-success {
            color: #155724;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 4px;
        }

        .message-warning {
            color: #856404;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 10px;
            border-radius: 4px;
        }

        .message-info {
            color: #004085;
            background-color: #cce5ff;
            border: 1px solid #b8daff;
            padding: 10px;
            border-radius: 4px;
        }
    </style>

    {% block page_specific_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">iRN System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                {% if user.is_authenticated %}
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item dropdown">
                        <button class="nav-link dropdown-toggle btn btn-link" 
                                id="navbarDropdown" 
                                data-bs-toggle="dropdown" 
                                aria-expanded="false"
                                style="text-decoration: none; border: none; background: none; color: white;">
                            <i class="fas fa-user me-1"></i>
                            {{ user.get_full_name|default:user.username }}
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="navbarDropdown">
                            <li>
                                <a class="dropdown-item" href="{% url 'users:profile' %}">
                                    <i class="fas fa-tachometer-alt me-2"></i>Profile
                                </a>
                            </li>
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <form method="post" action="{% url 'users:logout' %}" class="d-inline w-100">
                                    {% csrf_token %}
                                    <button type="submit" class="dropdown-item text-danger">
                                        <i class="fas fa-sign-out-alt me-2"></i>Logout
                                    </button>
                                </form>
                            </li>
                        </ul>
                    </li>
                </ul>
                {% else %}
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'users:register' %}">
                            <i class="fas fa-user-plus me-1"></i> Register
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'users:login' %}">
                            <i class="fas fa-sign-in-alt me-1"></i> Login
                        </a>
                    </li>
                </ul>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="{% url 'submission:dashboard' %}">
                                <i class="fas fa-tachometer-alt"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'submission:start_submission' %}">
                                <i class="fas fa-plus-circle"></i> Start New Submission
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:inbox' %}">
                                <i class="fas fa-inbox"></i> Inbox
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:sent_messages' %}">
                                <i class="fas fa-paper-plane"></i> Sent Messages
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:archived_messages' %}">
                                <i class="fas fa-archive"></i> Archived Messages
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'messaging:compose_message' %}">
                                <i class="fas fa-pen"></i> Compose Message
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Content Area -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <!-- Popup Overlay and Content -->
    <div id="popupOverlay" class="popup-overlay"></div>
    <div id="customPopup" class="custom-popup">
        <div class="popup-header">
            <h4>Notification</h4>
            <span class="popup-close" onclick="closePopup()">&times;</span>
        </div>
        <div class="popup-content" id="popupContent">
        </div>
        <div class="popup-footer">
            <button class="popup-button" onclick="closePopup()">OK</button>
        </div>
    </div>

    <!-- JavaScript Dependencies -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/dataTables.bootstrap4.min.js"></script>

    <!-- Base JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Enable all dropdowns
            var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
            var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
                return new bootstrap.Dropdown(dropdownToggleEl);
            });

            // Add hover effect for dropdown
            $('.nav-item.dropdown').hover(
                function() {
                    $(this).find('.dropdown-toggle').dropdown('show');
                },
                function() {
                    $(this).find('.dropdown-toggle').dropdown('hide');
                }
            );

            // Initialize popup for Django messages
            const messages = [
                {% for message in messages %}
                    {
                        text: "{{ message }}",
                        tags: "{{ message.tags }}"
                    },
                {% endfor %}
            ];
            
            if (messages.length > 0) {
                messages.forEach(function(message) {
                    showPopup(message.text, message.tags || 'info');
                });
            }
        });

        // Global popup functions
        function showPopup(message, type = 'info') {
            const popup = document.getElementById('customPopup');
            const overlay = document.getElementById('popupOverlay');
            const content = document.getElementById('popupContent');
            
            const messageElement = document.createElement('div');
            messageElement.className = `message-${type}`;
            messageElement.textContent = message;
            
            content.innerHTML = '';
            content.appendChild(messageElement);
            
            popup.style.display = 'block';
            overlay.style.display = 'block';
            
            document.addEventListener('keydown', handleEscapeKey);
        }
        
        function closePopup() {
            const popup = document.getElementById('customPopup');
            const overlay = document.getElementById('popupOverlay');
            popup.style.display = 'none';
            overlay.style.display = 'none';
            
            document.removeEventListener('keydown', handleEscapeKey);
        }
        
        function handleEscapeKey(e) {
            if (e.key === 'Escape') {
                closePopup();
            }
        }
        
        // Click outside to close popup
        document.getElementById('popupOverlay').addEventListener('click', closePopup);
    </script>

    {% block page_specific_js %}{% endblock %}
</body>
</html>{% extends 'users/base.html' %}
<p>If you forgot your password, send us an email using the email used for registration to aidi@khcc.jo and we will reset your password in 24 hours. You can</p>
{% load crispy_forms_tags %}
{% block title %}Login{% endblock %}
{% block content %}
<h1>Login</h1>
<form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit">Login</button>
</form>
{% endblock %}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}


{% block title %}Profile - {{ user.get_full_name|default:user.username }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>User Profile</h2>
                </div>
                <div class="card-body">
                    <form method="POST" enctype="multipart/form-data" novalidate>
                        {% csrf_token %}
                        {{ profile_form|crispy }}
                        <div class="mb-3 row">
                            <div class="col-sm-9 offset-sm-3">
                                <button type="submit" class="btn btn-primary">Save Changes</button>
                            </div>
                        </div>
                    </form>

                    <hr>

                    <h3 class="mt-4">Required Documents Status</h3>
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Document Type</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>GCP Certificate</td>
                                    <td>
                                        {% if user.userprofile.has_valid_gcp %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Expired/Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                                <tr>
                                    <td>QRC Certificate</td>
                                    <td>
                                        {% if user.userprofile.has_qrc %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Expired/Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                                <tr>
                                    <td>CTC Certificate</td>
                                    <td>
                                        {% if user.userprofile.has_ctc %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Expired/Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                                <tr>
                                    <td>CV</td>
                                    <td>
                                        {% if user.userprofile.has_cv %}
                                            <span class="badge bg-success">Valid</span>
                                        {% else %}
                                            <span class="badge bg-danger">Missing</span>
                                        {% endif %}
                                    </td>
                                    <td><a href="{% url 'users:upload_document' %}" class="btn btn-sm btn-primary">Upload</a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Register{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Register</h2>
                </div>
                <div class="card-body">
                    {% if messages %}
                    <div class="messages">
                        {% for message in messages %}
                        <div class="alert alert-{{ message.tags }}">
                            {{ message }}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    <form method="post" enctype="multipart/form-data" novalidate>
                        {% csrf_token %}
                        {{ user_form|crispy }}
                        {{ profile_form|crispy }}
                        <div class="alert alert-info">
                            <small>{{ usage_agreement }}</small>
                        </div>
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-user-plus me-2"></i>Register
                            </button>
                            <a href="{% url 'users:login' %}" class="btn btn-link text-center">
                                Already have an account? Login here
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Upload Document{% endblock %}
{% block content %}
<h1>Upload Document</h1>
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form|crispy }}
    <button type="submit">Upload</button>
</form>
<p>Or <a href="https://khcc.jo">Skip and go to khcc.jo</a></p>
{% endblock %}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}
{% block title %}My Documents{% endblock %}
{% block content %}
<h1>My Documents</h1>
{% if documents %}
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Document Type</th>
                <th>Uploaded On</th>
                <th>Issued On</th>
                <th>Expires On</th>
                <th>Comments</th>
            </tr>
        </thead>
        <tbody>
        {% for doc_info in documents %}
            <tr {% if doc_info.days_until_expiry < 30 and doc_info.days_until_expiry >= 0 %}class="text-danger"{% endif %}>
                <td>
                    <a href="{% url 'users:display_document' doc_info.document.id %}" class="document-link" data-document-type="{{ doc_info.document.get_document_type_display }}" data-file-extension="{{ doc_info.file_extension }}" {% if doc_info.file_extension == '.pdf' %}target="_blank"{% endif %}>
                        {% if doc_info.document.document_type == 'Other' %}
                            {{ doc_info.document.other_document_name }}
                        {% else %}
                            {{ doc_info.document.get_document_type_display }}
                        {% endif %}
                    </a>
                </td>
                <td>{{ doc_info.document.uploaded_at|date:"F d, Y" }}</td>
                <td>{{ doc_info.document.issue_date|date:"F d, Y" }}</td>
                <td>{{ doc_info.document.expiry_date|date:"F d, Y" }}</td>
                <td>
                    {% if doc_info.days_until_expiry is not None %}
                        Days until expiry: {{ doc_info.days_until_expiry }}
                    {% endif %}
                </td>
            </tr>
        {% endfor %}
        </tbody>
    </table>

    <!-- Modal for image preview -->
    <div class="modal fade" id="imageModal" tabindex="-1" role="dialog" aria-labelledby="imageModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="imageModalLabel"></h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <img id="imageFrame" style="width: 100%;" />
                </div>
            </div>
        </div>
    </div>

    <script>
        $(document).ready(function() {
            $('.document-link').click(function(e) {
                var fileExtension = $(this).data('file-extension');
                var documentType = $(this).data('document-type');
                
                if (fileExtension === '.pdf') {
                    // For PDF files, let the browser open it in a new tab
                    return true;
                } else if (['.jpg', '.jpeg', '.png', '.gif'].includes(fileExtension)) {
                    // For image files, show in modal
                    e.preventDefault();
                    var documentUrl = $(this).attr('href');
                    $('#imageModalLabel').text(documentType);
                    $('#imageFrame').attr('src', documentUrl);
                    $('#imageModal').modal('show');
                } else {
                    // For other file types, let the browser handle it
                    return true;
                }
            });
        });
    </script>
{% else %}
    <p>You haven't uploaded any documents yet.</p>
{% endif %}
<a href="{% url 'users:upload_document' %}" class="btn btn-primary">Upload New Document</a>
{% endblock %}
