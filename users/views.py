# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
import os
import logging
from datetime import date, datetime
from pathlib import Path

from .forms import (
    UserRegistrationForm, 
    LoginForm, 
    DocumentForm, 
    UserProfileForm,
    UserEditForm,
    CustomPasswordChangeForm
)
from .models import UserProfile, Role, Document
# Set up loggers
users_logger = logging.getLogger('IRN.users')
security_logger = logging.getLogger('IRN.security')

# File security configuration
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(uploaded_file):
    """Validate file size and type"""
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(f'File size cannot exceed {MAX_FILE_SIZE/1024/1024}MB')

    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f'Unsupported file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS.keys())}')

    content_type = uploaded_file.content_type
    if content_type not in ALLOWED_EXTENSIONS.values():
        raise ValidationError('File type does not match its extension')

    return True

# views.py (update the profile view)
@login_required
def profile(request):
    """Handle user profile view and updates"""
    try:
        today = date.today()
        if request.method == 'POST':
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(
                request.POST, 
                request.FILES, 
                instance=request.user.userprofile
            )
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            
            # Flag to track if password form was filled
            password_changed = any(request.POST.get(key) for key in password_form.fields.keys())
            
            # Validate forms
            forms_valid = user_form.is_valid() and profile_form.is_valid()
            if password_changed:
                forms_valid = forms_valid and password_form.is_valid()

            if forms_valid:
                try:
                    with transaction.atomic():
                        user_form.save()
                        profile_form.save()
                        
                        if password_changed and password_form.is_valid():
                            password_form.save()
                            # Re-authenticate the user
                            update_session_auth_hash(request, request.user)
                            messages.success(request, 'Password updated successfully.')
                            
                        users_logger.info(f"Profile updated: {request.user.username}")
                        messages.success(request, 'Profile updated successfully.')
                        return redirect('users:profile')
                except Exception as e:
                    users_logger.error(f"Profile update error: {str(e)}", exc_info=True)
                    messages.error(request, 'An error occurred while updating your profile.')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            user_form = UserEditForm(instance=request.user)
            profile_form = UserProfileForm(instance=request.user.userprofile)
            password_form = CustomPasswordChangeForm(request.user)

        documents = [{
            'document': doc,
            'days_until_expiry': (doc.expiry_date - today).days if doc.expiry_date else None,
            'is_expiring_soon': doc.expiry_date and (doc.expiry_date - today).days < 30 if doc.expiry_date else False
        } for doc in request.user.documents.all()]

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'today': today,
            'documents': documents,
        }
        return render(request, 'users/profile.html', context)
        
    except Exception as e:
        users_logger.error(f"Profile view error: {request.user.username} - {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please try again later.')
        return redirect('users:profile')

@require_http_methods(["GET", "POST"])
def register(request):
    """Handle new user registration"""
    if request.user.is_authenticated:
        return redirect('messaging:inbox')
        
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Create user
                    user = user_form.save(commit=False)
                    full_name_parts = user_form.cleaned_data['full_name'].split()
                    user.first_name = full_name_parts[0]
                    user.last_name = ' '.join(full_name_parts[1:]) if len(full_name_parts) > 1 else ''
                    user.save()

                    # Update profile
                    profile = UserProfile.objects.get(user=user)
                    for field in profile_form.cleaned_data:
                        setattr(profile, field, profile_form.cleaned_data[field])
                    profile.save()

                    users_logger.info(f"New user registered: {user.username}")
                    messages.success(request, 'Registration successful. Awaiting approval from administrator.')
                    return redirect('users:login')

            except Exception as e:
                users_logger.error(f"Registration error: {str(e)}", exc_info=True)
                messages.error(request, 'An error occurred during registration. Please try again.')
                if isinstance(e, IntegrityError):
                    messages.error(request, 'A user with this username or email already exists.')
        else:
            if user_form.errors:
                users_logger.warning(f"User form validation errors: {user_form.errors}")
            if profile_form.errors:
                users_logger.warning(f"Profile form validation errors: {profile_form.errors}")
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'users/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'usage_agreement': 'By registering, you agree to the terms and conditions of use.',
    })

@require_http_methods(["GET", "POST"])
def user_login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('messaging:inbox')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    security_logger.info(f"Login successful: {username}")
                    return redirect('messaging:inbox')
                else:
                    security_logger.warning(f"Login attempt to inactive account: {username}")
                    messages.error(request, 'Your account is not active.')
            else:
                security_logger.warning(f"Failed login attempt: {username}")
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please provide both username and password')
    
    return render(request, 'users/login.html')

@login_required
def user_logout(request):
    """Handle user logout"""
    username = request.user.username
    logout(request)
    security_logger.info(f"User logged out: {username}")
    messages.success(request, 'You have been successfully logged out.')
    return redirect('users:login')

@login_required
@require_http_methods(["GET", "POST"])
def upload_document(request):
    """Handle document uploads"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.user = request.user
                
                # Validate file
                validate_file(request.FILES['file'])
                document.save()
                
                security_logger.info(
                    f"Document uploaded: {document.get_document_type_display()} by {request.user.username}"
                )
                
                messages.success(request, 'Document uploaded successfully.')
                return redirect('users:view_documents')
                
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                security_logger.error(f"Document upload error: {str(e)}", exc_info=True)
                messages.error(request, 'Error uploading document. Please try again.')
    else:
        form = DocumentForm()
    
    return render(request, 'users/upload_document.html', {
        'form': form,
        'allowed_types': list(ALLOWED_EXTENSIONS.keys()),
        'max_size_mb': MAX_FILE_SIZE / (1024 * 1024)
    })

@login_required
def view_documents(request):
    """Display user's documents"""
    try:
        documents = request.user.documents.all()
        documents_with_expiry = [{
            'document': document,
            'days_until_expiry': (document.expiry_date - date.today()).days if document.expiry_date else None,
            'file_extension': os.path.splitext(document.file.name)[1].lower()
        } for document in documents]
        
        return render(request, 'users/view_documents.html', {'documents': documents_with_expiry})
        
    except Exception as e:
        users_logger.error(f"Error viewing documents: {str(e)}", exc_info=True)
        messages.error(request, 'Error loading documents. Please try again.')
        return redirect('users:profile')

@login_required
def display_document(request, document_id):
    """Display a specific document"""
    try:
        # Get document and verify ownership
        document = get_object_or_404(Document, id=document_id)
        
        # Check if the user has permission to view this document
        if document.user != request.user and not request.user.is_staff:
            raise PermissionDenied("You don't have permission to view this document.")

        # Get the file path and verify it exists
        if not document.file:
            raise FileNotFoundError("Document file not found in database")
            
        file_path = document.file.path
        
        if not os.path.exists(file_path):
            users_logger.error(f"Physical file missing for document {document_id}: {file_path}")
            raise FileNotFoundError(f"Document file not found on disk: {file_path}")

        # Determine content type
        file_ext = os.path.splitext(document.file.name)[1].lower()
        content_type = ALLOWED_EXTENSIONS.get(
            file_ext, 
            mimetypes.guess_type(document.file.name)[0] or 'application/octet-stream'
        )

        try:
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type
            )
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(document.file.name)}"'
            
            users_logger.info(
                f"Document successfully served: {document.get_document_type_display()} "
                f"(ID: {document_id}) to user {request.user.username}"
            )
            return response

        except IOError as e:
            users_logger.error(f"IOError reading document {document_id}: {str(e)}")
            return HttpResponseServerError("Error reading document file")

    except Document.DoesNotExist:
        users_logger.warning(f"Attempt to access non-existent document {document_id}")
        return HttpResponseNotFound("Document not found")
        
    except PermissionDenied as e:
        security_logger.warning(
            f"Unauthorized document access attempt: User {request.user.username} "
            f"tried to access document {document_id}"
        )
        messages.error(request, str(e))
        return redirect('users:view_documents')
        
    except FileNotFoundError as e:
        users_logger.error(f"File not found for document {document_id}: {str(e)}")
        messages.error(request, "Document file not found")
        return redirect('users:view_documents')
        
    except Exception as e:
        users_logger.error(
            f"Unexpected error displaying document {document_id}: {str(e)}", 
            exc_info=True
        )
        messages.error(request, "An error occurred while displaying the document")
        return redirect('users:view_documents')

@login_required
def role_autocomplete(request):
    """Handle role autocomplete functionality"""
    try:
        term = request.GET.get('term', '').strip()
        
        if len(term) < 2:
            return JsonResponse([], safe=False)

        roles = Role.objects.filter(name__icontains=term)[:10]
        results = [{'id': role.id, 'label': role.name} for role in roles]
        
        return JsonResponse(results, safe=False)
        
    except Exception as e:
        users_logger.error(f"Role autocomplete error: {str(e)}", exc_info=True)
        return JsonResponse([], safe=False)