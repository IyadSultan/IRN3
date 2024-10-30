# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm, DocumentForm, UserProfileForm
from django.contrib import messages
from datetime import date
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse
import os
from django.db import transaction

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













