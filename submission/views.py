# submission/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dal import autocomplete
import json

from .models import Submission, CoInvestigator, ResearchAssistant, FormDataEntry
from .forms import SubmissionForm, ResearchAssistantForm, CoInvestigatorForm
from .utils import has_edit_permission, check_researcher_documents
from forms_builder.models import DynamicForm
from messaging.models import Message

@login_required
def start_submission(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            submission = form.save(commit=False)
            is_pi = form.cleaned_data['is_primary_investigator']
            
            if is_pi:
                submission.primary_investigator = request.user
            else:
                pi_user = form.cleaned_data['primary_investigator']
                if pi_user:
                    submission.primary_investigator = pi_user
                else:
                    messages.error(request, 'Please select a primary investigator.')
                    return render(request, 'submission/start_submission.html', {'form': form})
            
            submission.save()
            messages.success(request, f'Temporary submission ID {submission.temporary_id} generated.')
            
            # Send notification message
            message = Message.objects.create(
                sender=request.user,
                subject='Temporary Submission ID Generated',
                body=f'Your submission has been created with temporary ID {submission.temporary_id}.'
            )
            message.recipients.add(request.user)
            
            # Handle different actions
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                # Redirect to the research assistant page
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
    else:
        form = SubmissionForm()
    
    return render(request, 'submission/start_submission.html', {'form': form})

@login_required
def add_research_assistant(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
        
    if request.method == 'POST':
        form = ResearchAssistantForm(request.POST)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            assistant_user = form.cleaned_data['assistant']
            ResearchAssistant.objects.create(
                submission=submission,
                user=assistant_user,
                can_submit=form.cleaned_data['can_submit'],
                can_edit=form.cleaned_data['can_edit'],
                can_view_communications=form.cleaned_data['can_view_communications']
            )
            messages.success(request, 'Research assistant added.')
            
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                # Proceed to co-investigator page
                return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
            else:
                # Stay on the same page to add more research assistants
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
    else:
        form = ResearchAssistantForm()
        
    assistants = submission.research_assistants.all()
    return render(request, 'submission/add_research_assistant.html', {
        'form': form,
        'assistants': assistants,
        'submission': submission
    })

@login_required
def add_coinvestigator(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
        
    if request.method == 'POST':
        form = CoInvestigatorForm(request.POST)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            investigator_user = form.cleaned_data['investigator']
            role_in_study = form.cleaned_data['role_in_study']
            order = submission.coinvestigators.count() + 1
            
            CoInvestigator.objects.create(
                submission=submission,
                user=investigator_user,
                role_in_study=role_in_study,
                can_submit=form.cleaned_data['can_submit'],
                can_edit=form.cleaned_data['can_edit'],
                can_view_communications=form.cleaned_data['can_view_communications'],
                order=order
            )
            messages.success(request, 'Co-investigator added successfully.')
            
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                # Proceed to forms page
                return redirect('submission:submission_forms', submission_id=submission.temporary_id)
            else:
                # Stay on the same page to add more co-investigators
                return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
    else:
        form = CoInvestigatorForm()
    
    coinvestigators = submission.coinvestigators.all().order_by('order')
    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'coinvestigators': coinvestigators,
        'submission': submission
    })

@login_required
def submission_forms(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
    if submission.status not in ['draft', 'under_revision']:
        messages.error(request, "You cannot edit forms after submission.")
        return redirect('submission:dashboard')
    dynamic_forms = submission.study_type.forms.all()
    if request.method == 'POST':
        for dynamic_form in dynamic_forms:
            django_form_class = generate_django_form(dynamic_form)
            form_instance = django_form_class(request.POST, prefix=f'form_{dynamic_form.id}')
            if form_instance.is_valid():
                for field_name, value in form_instance.cleaned_data.items():
                    FormDataEntry.objects.update_or_create(
                        submission=submission,
                        form=dynamic_form,
                        field_name=field_name,
                        defaults={'value': value, 'version': submission.version}
                    )
                messages.success(request, f'Form "{dynamic_form.name}" saved.')
            else:
                messages.error(request, f'Error in form "{dynamic_form.name}".')
        action = request.POST.get('action')
        if action == 'save_exit':
            return redirect('submission:dashboard')
        elif action == 'save_continue':
            # Proceed to next step or reload forms
            pass
        elif action == 'exit_no_save':
            return redirect('submission:dashboard')
        elif action == 'submit':
            # Check researcher documents before submission
            all_good, missing_docs = check_researcher_documents(submission)
            if all_good:
                submission.status = 'submitted'
                submission.date_submitted = timezone.now()
                submission.version += 1
                submission.save()
                messages.success(request, 'Submission completed successfully.')
                # Send messages, lock editing, etc.
                # Notify PI and Research Assistants
                message = Message.objects.create(
                    sender=request.user,
                    subject='Study Submitted',
                    body=f'The study "{submission.title}" has been submitted.'
                )
                message.recipients.add(submission.primary_investigator)
                for assistant in submission.research_assistants.all():
                    assistant_message = Message.objects.create(
                        sender=request.user,
                        subject='Study Submitted',
                        body=f'The study "{submission.title}" has been submitted.'
                    )
                    assistant_message.recipients.add(assistant.user)
                return redirect('submission:dashboard')
            else:
                messages.error(request, 'Cannot submit due to missing or expired documents: ' + ', '.join(missing_docs))
    else:
        # Render forms
        forms_list = []
        for dynamic_form in dynamic_forms:
            django_form_class = generate_django_form(dynamic_form)
            # Pre-fill form data if it exists
            initial_data = {
                entry.field_name: entry.value
                for entry in FormDataEntry.objects.filter(
                    submission=submission, form=dynamic_form, version=submission.version
                )
            }
            form_instance = django_form_class(initial=initial_data, prefix=f'form_{dynamic_form.id}')
            forms_list.append((dynamic_form, form_instance))
    return render(request, 'submission/submission_forms.html', {
        'forms_list': forms_list,
        'submission': submission
    })

def generate_django_form(dynamic_form):
    from django import forms
    fields = {}
    for field in dynamic_form.fields.all():
        # Map DynamicForm field types to Django form fields
        if field.field_type == 'text':
            fields[field.name] = forms.CharField(
                max_length=field.max_length or 255,
                required=False,
                initial=field.default_value
            )
        elif field.field_type == 'number':
            fields[field.name] = forms.DecimalField(
                required=False,
                initial=field.default_value
            )
        elif field.field_type == 'date':
            fields[field.name] = forms.DateField(
                required=False,
                initial=field.default_value,
                widget=forms.DateInput(attrs={'type': 'date'})
            )
        elif field.field_type in ['choice', 'dropdown']:
            choices = [(choice.strip(), choice.strip()) for choice in field.choices.split(',')]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                required=False,
                initial=field.default_value
            )
        # Add other field types as needed
    DjangoForm = type(f'DynamicForm_{dynamic_form.id}', (forms.Form,), fields)
    return DjangoForm

@login_required
def dashboard(request):
    submissions = Submission.objects.filter(
        primary_investigator=request.user
    ).select_related('study_type')
    return render(request, 'submission/dashboard.html', {'submissions': submissions})

@login_required
def edit_submission(request, submission_id):
    print(f"Edit submission view called with ID: {submission_id}")  # Debug print
    submission = get_object_or_404(Submission, pk=submission_id)
    print(f"Submission found: {submission}")  # Debug print
    
    # Check permissions
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
    
    # Check if submission is editable
    if submission.status not in ['draft', 'under_revision']:
        messages.error(request, "This submission cannot be edited.")
        return redirect('submission:dashboard')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submission updated successfully.')
            return redirect('submission:dashboard')
    else:
        form = SubmissionForm(instance=submission)
    
    # Add print statement for debugging
    print("Rendering edit_submission.html with form:", form)
    
    return render(request, 'submission/edit_submission.html', {
        'form': form,
        'submission': submission,
        'page_title': 'Edit Submission'
    })

class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()
        if self.q:
            qs = qs.filter(username__icontains=self.q)
        return qs

@login_required
def download_submission_pdf(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="submission_{submission.temporary_id}.pdf"'
    
    # Create the PDF object using ReportLab
    p = canvas.Canvas(response, pagesize=letter)
    
    # Add content to the PDF
    p.drawString(100, 750, f"Submission ID: {submission.temporary_id}")
    p.drawString(100, 730, f"Title: {submission.title}")
    p.drawString(100, 710, f"Primary Investigator: {submission.primary_investigator.get_full_name()}")
    p.drawString(100, 690, f"Status: {submission.get_status_display()}")
    
    # Add more content as needed
    
    p.showPage()
    p.save()
    return response

@login_required
def update_coinvestigator_order(request, submission_id):
    if request.method == 'POST':
        submission = get_object_or_404(Submission, pk=submission_id)
        
        if not has_edit_permission(request.user, submission):
            return JsonResponse({'error': 'Permission denied'}, status=403)
            
        try:
            order = json.loads(request.POST.get('order', '[]'))
            for index, coinvestigator_id in enumerate(order):
                CoInvestigator.objects.filter(
                    id=coinvestigator_id, 
                    submission=submission
                ).update(order=index)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
