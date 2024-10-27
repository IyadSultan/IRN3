# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm, DocumentForm, UserProfileForm
from django.contrib import messages
from datetime import date
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
import os
import mimetypes
from django.conf import settings


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Registration successful. Awaiting approval from administrator.')
            return redirect('users:login')
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

# @login_required
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
    for document in documents:
        if document.expiry_date:
            document.days_until_expiry = (document.expiry_date - date.today()).days
        else:
            document.days_until_expiry = None
        document.file_extension = os.path.splitext(document.file.name)[1].lower()
    context = {'documents': documents}
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
        # For non-PDF files, you might want to serve them differently
        return FileResponse(open(file_path, 'rb'))

# @login_required
# def view_certificates(request):
#     documents = request.user.documents.all()
#     for document in documents:
#         if document.expiry_date:
#             document.days_until_expiry = (document.expiry_date - date.today()).days
#         else:
#             document.days_until_expiry = None
#     context = {'documents': documents}
#     return render(request, 'users/view_certificates.html', context)













