from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from dal import autocomplete
import json
from io import BytesIO
from .utils import PDFGenerator
from .utils.pdf_generator import generate_submission_pdf
from django.urls import reverse

from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
)
from .forms import (
    SubmissionForm,
    ResearchAssistantForm,
    CoInvestigatorForm,
    DocumentForm,
    generate_django_form,
)
from .utils import (
    has_edit_permission,
    check_researcher_documents,
    get_next_form,
    get_previous_form,
)
from forms_builder.models import DynamicForm
from messaging.models import Message, MessageAttachment
from users.models import SystemSettings
from django import forms

import logging
logger = logging.getLogger(__name__)

from django.db.models import Q

@login_required
def dashboard(request):
    """Display user's submissions dashboard."""
    from django.db.models import Max
    
    submissions = Submission.objects.filter(
        primary_investigator=request.user
    ).select_related(
        'primary_investigator',
        'primary_investigator__userprofile'
    )
    
    # Get the actual latest version for each submission from FormDataEntry
    for submission in submissions:
        latest_version = FormDataEntry.objects.filter(
            submission=submission
        ).values('version').aggregate(Max('version'))['version__max']
        submission.actual_version = latest_version or 1  # Use 1 if no entries found

    return render(request, 'submission/dashboard.html', {'submissions': submissions})

@login_required
def edit_submission(request, submission_id):
    """Redirect to start_submission with existing submission ID."""
    return redirect('submission:start_submission_with_id', submission_id=submission_id)

@login_required
def start_submission(request, submission_id=None):
    """Start or edit a submission."""
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        print(f"Found submission with PI: {submission.primary_investigator}")
        print(f"Current user: {request.user}")
        
        if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to edit this submission.")
            return redirect('submission:dashboard')
        
        # Only set initial data for primary_investigator, not is_primary_investigator
        initial_data = {
            'primary_investigator': submission.primary_investigator
        }
    else:
        submission = None
        initial_data = {}

    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        form = SubmissionForm(request.POST, instance=submission)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            submission = form.save(commit=False)
            # Get is_pi directly from POST data instead of cleaned_data
            is_pi = request.POST.get('is_primary_investigator') == 'on'
            
            if is_pi:
                submission.primary_investigator = request.user
            else:
                pi_user = form.cleaned_data.get('primary_investigator')
                if not pi_user:
                    messages.error(request, 'Please select a primary investigator.')
                    return render(request, 'submission/start_submission.html', {
                        'form': form,
                        'submission': submission
                    })
                submission.primary_investigator = pi_user
                
            submission.save()
            messages.success(request, f'Temporary submission ID {submission.temporary_id} generated.')
            
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
    else:
        form = SubmissionForm(instance=submission, initial=initial_data)
        # Explicitly set is_primary_investigator based on current state
        if submission and submission.primary_investigator == request.user:
            form.fields['is_primary_investigator'].initial = True
        else:
            form.fields['is_primary_investigator'].initial = False

    return render(request, 'submission/start_submission.html', {
        'form': form,
        'submission': submission,
    })

from django import forms
from django.contrib.auth.models import User
from .models import ResearchAssistant  # Add this import

@login_required
def add_research_assistant(request, submission_id):
    """Add or manage research assistants for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_assistant':
            assistant_id = request.POST.get('assistant_id')
            if assistant_id:
                try:
                    assistant = ResearchAssistant.objects.get(id=assistant_id, submission=submission)
                    assistant.delete()
                    messages.success(request, 'Research assistant removed successfully.')
                except ResearchAssistant.DoesNotExist:
                    messages.error(request, 'Research assistant not found.')
            return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:start_submission_with_id', submission_id=submission.temporary_id)
            elif action == 'exit_no_save':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        form = ResearchAssistantForm(request.POST, submission=submission)
        if form.is_valid():
            assistant = form.cleaned_data.get('assistant')
            if assistant:
                ResearchAssistant.objects.create(
                    submission=submission,
                    user=assistant,
                    can_submit=form.cleaned_data.get('can_submit', False),
                    can_edit=form.cleaned_data.get('can_edit', False),
                    can_view_communications=form.cleaned_data.get('can_view_communications', False)
                )
                messages.success(request, 'Research assistant added successfully.')
                
                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please select a research assistant.')
    else:
        form = ResearchAssistantForm()

    assistants = ResearchAssistant.objects.filter(submission=submission)
    return render(request, 'submission/add_research_assistant.html', {
        'form': form,
        'submission': submission,
        'assistants': assistants
    })

@login_required
def add_coinvestigator(request, submission_id):
    """Add or manage co-investigators for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_coinvestigator':
            coinvestigator_id = request.POST.get('coinvestigator_id')
            if coinvestigator_id:
                try:
                    coinvestigator = CoInvestigator.objects.get(id=coinvestigator_id, submission=submission)
                    coinvestigator.delete()
                    messages.success(request, 'Co-investigator removed successfully.')
                except CoInvestigator.DoesNotExist:
                    messages.error(request, 'Co-investigator not found.')
            return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        if action in ['back', 'exit_no_save', 'save_continue']:
            if action == 'back':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
            elif action == 'exit_no_save':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                first_form = submission.study_type.forms.order_by('order').first()
                if first_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id,
                                  form_id=first_form.id)
                else:
                    return redirect('submission:submission_review', 
                                  submission_id=submission.temporary_id)

        form = CoInvestigatorForm(request.POST, submission=submission)
        if form.is_valid():
            investigator = form.cleaned_data.get('investigator')
            selected_roles = form.cleaned_data.get('roles')
            
            if investigator:
                # Create the coinvestigator instance
                coinvestigator = CoInvestigator.objects.create(
                    submission=submission,
                    user=investigator,
                    can_submit=form.cleaned_data.get('can_submit', False),
                    can_edit=form.cleaned_data.get('can_edit', False),
                    can_view_communications=form.cleaned_data.get('can_view_communications', False)
                )
                
                # Add the selected roles
                if selected_roles:
                    coinvestigator.roles.set(selected_roles)
                
                messages.success(request, 'Co-investigator added successfully.')
                
                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please select a co-investigator and specify their roles.')
    else:
        form = CoInvestigatorForm()

    coinvestigators = CoInvestigator.objects.filter(submission=submission)
    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'submission': submission,
        'coinvestigators': coinvestigators
    })

@login_required
def submission_form(request, submission_id, form_id):
    """Handle dynamic form submission and display."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    dynamic_form = get_object_or_404(DynamicForm, pk=form_id)
    action = request.POST.get('action')

    def process_field_value(value, field_type):
        """Helper function to process field values based on field type."""
        if field_type == 'checkbox':
            try:
                if isinstance(value, str):
                    if value.startswith('['):
                        return json.loads(value)
                    # Handle comma-separated string values
                    return [v.strip() for v in value.split(',') if v.strip()]
                return value
            except json.JSONDecodeError:
                return []
        return value

    if request.method == 'POST':
        # Handle navigation actions without form processing
        if action in ['back', 'exit_no_save']:
            if action == 'back':
                previous_form = get_previous_form(submission, dynamic_form)
                if previous_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id, 
                                  form_id=previous_form.id)
                return redirect('submission:add_coinvestigator', 
                              submission_id=submission.temporary_id)
            return redirect('submission:dashboard')

        # Create form instance without validation
        DynamicFormClass = generate_django_form(dynamic_form)
        
        # Save all form fields without validation
        for field_name, field in DynamicFormClass.base_fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                # Handle multiple choice fields (including checkboxes)
                values = request.POST.getlist(f'form_{dynamic_form.id}-{field_name}')
                value = json.dumps(values) if values else '[]'
            else:
                value = request.POST.get(f'form_{dynamic_form.id}-{field_name}', '')
                
            FormDataEntry.objects.update_or_create(
                submission=submission,
                form=dynamic_form,
                field_name=field_name,
                version=submission.version,
                defaults={'value': value}
            )
        
        # Handle post-save navigation
        if action == 'save_exit':
            return redirect('submission:dashboard')
        elif action == 'save_continue':
            next_form = get_next_form(submission, dynamic_form)
            if next_form:
                return redirect('submission:submission_form', 
                              submission_id=submission.temporary_id, 
                              form_id=next_form.id)
            return redirect('submission:submission_review', 
                          submission_id=submission.temporary_id)
    
    # GET request handling
    DynamicFormClass = generate_django_form(dynamic_form)
    current_data = {}
    
    # Get current version's data
    for entry in FormDataEntry.objects.filter(
        submission=submission,
        form=dynamic_form,
        version=submission.version
    ):
        field = DynamicFormClass.base_fields.get(entry.field_name)
        if field:
            if isinstance(field, forms.MultipleChoiceField):
                try:
                    current_data[entry.field_name] = process_field_value(
                        entry.value, 
                        getattr(dynamic_form.fields.get(name=entry.field_name), 'field_type', None)
                    )
                except json.JSONDecodeError:
                    current_data[entry.field_name] = []
            else:
                current_data[entry.field_name] = entry.value

    # If no current data and not version 1, get previous version's data
    if not current_data and submission.version > 1 and not submission.is_locked:
        for entry in FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version - 1
        ):
            field = DynamicFormClass.base_fields.get(entry.field_name)
            if field:
                if isinstance(field, forms.MultipleChoiceField):
                    try:
                        current_data[entry.field_name] = process_field_value(
                            entry.value,
                            getattr(dynamic_form.fields.get(name=entry.field_name), 'field_type', None)
                        )
                    except json.JSONDecodeError:
                        current_data[entry.field_name] = []
                else:
                    current_data[entry.field_name] = entry.value

    # Create form instance with processed data
    form_instance = DynamicFormClass(
        initial=current_data,
        prefix=f'form_{dynamic_form.id}'
    )

    context = {
        'form': form_instance,
        'submission': submission,
        'dynamic_form': dynamic_form,
        'previous_form': get_previous_form(submission, dynamic_form),
    }
    return render(request, 'submission/dynamic_form.html', context)


@login_required
def submission_review(request, submission_id):
    """Review submission before final submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    print(submission)
    if submission.is_locked and not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')

    missing_documents = check_researcher_documents(submission)
    
    validation_errors = {}
    
    # Validate all forms
    for dynamic_form in submission.study_type.forms.order_by('order'):
        django_form_class = generate_django_form(dynamic_form)
        entries = FormDataEntry.objects.filter(
            submission=submission, 
            form=dynamic_form, 
            version=submission.version
        )
        saved_data = {
            f'form_{dynamic_form.id}-{entry.field_name}': entry.value
            for entry in entries
        }
        
        form_instance = django_form_class(data=saved_data, prefix=f'form_{dynamic_form.id}')
        is_valid = True
        errors = {}
        
        for field_name, field in form_instance.fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                field_key = f'form_{dynamic_form.id}-{field_name}'
                field_value = saved_data.get(field_key)
                if not field_value and field.required:
                    is_valid = False
                    errors[field_name] = ['Please select at least one option']
            else:
                field_value = form_instance.data.get(f'form_{dynamic_form.id}-{field_name}')

                if field.required and not field_value:
                    is_valid = False
                    errors[field_name] = ['This field is required']

        if not is_valid:
            validation_errors[dynamic_form.name] = errors

    documents = submission.documents.all()
    doc_form = DocumentForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit_final':
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
            else:
                try:
                    # Lock submission and update status
                    submission.is_locked = True
                    submission.status = 'submitted'
                    submission.date_submitted = timezone.now()
                    # Don't increment version yet
                    submission.save()
                    
                    # Create version history entry starting with version 1
                    VersionHistory.objects.create(
                        submission=submission,
                        version=1,  # Start with version 1
                        status=submission.status,
                        date=timezone.now(),
                    )

                    # Get PI's full name
                    pi_full_name = submission.primary_investigator.userprofile.full_name or submission.primary_investigator.get_full_name()

                    # Create confirmation message with personalized greeting
                    message = Message.objects.create(
                        sender=request.user,
                        subject=f'Submission {submission.temporary_id} - Version 1 Confirmation',
                        body=f'Dear {pi_full_name},\n\nYour submission (ID: {submission.temporary_id}) has been successfully submitted. Please find the attached PDF for your records.',
                        study_name=submission.title if hasattr(submission, 'title') else None,
                    )
                    message.recipients.add(submission.primary_investigator)
                    
                    # Generate PDF for version 1
                    current_version = 1
                    logger.info(f"Generating PDF for submission {submission.temporary_id} version {current_version}")
                    
                    buffer = generate_submission_pdf(
                        submission=submission,
                        version=current_version,
                        user=request.user,
                        as_buffer=True
                    )
                    
                    if not buffer:
                        raise ValueError(f"Failed to generate PDF for version {current_version}")
                    
                    pdf_filename = f"submission_{submission.temporary_id}_v{current_version}.pdf"
                    pdf_content = ContentFile(buffer.getvalue())
                    
                    attachment = MessageAttachment(
                        message=message,
                        filename=pdf_filename
                    )
                    attachment.file.save(pdf_filename, pdf_content, save=True)
                    
                    # Now increment the version for future revisions
                    submission.version = 2  # Next version will be 2
                    submission.save()
                    
                    messages.success(request, 'Submission has been finalized and locked. A confirmation message has been sent.')
                    
                except Exception as e:
                    logger.error(f"Error in submission finalization process: {str(e)}")
                    logger.error("Error details:", exc_info=True)
                    messages.warning(request, 'Submission completed but there was an error sending the confirmation message.')
                
                return redirect('submission:dashboard')

        elif action == 'back':
            last_form = submission.study_type.forms.order_by('-order').first()
            if last_form:
                return redirect('submission:submission_form',
                              submission_id=submission.temporary_id,
                              form_id=last_form.id)
            return redirect('submission:add_coinvestigator',
                          submission_id=submission.temporary_id)

        elif action == 'exit_no_save':
            return redirect('submission:dashboard')

        elif action == 'upload_document':
            doc_form = DocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                document = doc_form.save(commit=False)
                document.submission = submission
                document.uploaded_by = request.user
                
                ext = document.file.name.split('.')[-1].lower()
                if ext in Document.ALLOWED_EXTENSIONS:
                    document.save()
                    messages.success(request, 'Document uploaded successfully.')
                else:
                    messages.error(
                        request,
                        f'Invalid file type: .{ext}. Allowed types are: {", ".join(Document.ALLOWED_EXTENSIONS)}'
                    )
            else:
                messages.error(request, 'Please correct the errors in the document form.')

    context = {
        'submission': submission,
        'missing_documents': missing_documents,
        'validation_errors': validation_errors,
        'documents': documents,
        'doc_form': doc_form,
    }

    return render(request, 'submission/submission_review.html', context)


@login_required
def document_delete(request, submission_id, document_id):
    """Delete a document from a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    document = get_object_or_404(Document, pk=document_id, submission=submission)
    
    if request.user == document.uploaded_by or has_edit_permission(request.user, submission):
        document.file.delete()
        document.delete()
        messages.success(request, 'Document deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this document.')
    
    return redirect('submission:submission_review', submission_id=submission_id)

@login_required
def version_history(request, submission_id):
    """View version history of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    histories = submission.version_histories.order_by('-version')
    return render(request, 'submission/version_history.html', {
        'submission': submission,
        'histories': histories,
    })

@login_required
def compare_versions(request, submission_id, version1, version2):
    """Compare two versions of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    comparison_data = []
    
    for form in submission.study_type.forms.all():
        entries_v1 = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version1
        ).select_related('form')
        
        entries_v2 = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version2
        ).select_related('form')

        data_v1 = {entry.field_name: entry.value for entry in entries_v1}
        data_v2 = {entry.field_name: entry.value for entry in entries_v2}

        field_definitions = {
            field.name: field.displayed_name 
            for field in form.fields.all()
        }

        form_changes = []
        all_fields = set(data_v1.keys()) | set(data_v2.keys())
        
        for field in all_fields:
            displayed_name = field_definitions.get(field, field)
            value1 = data_v1.get(field, 'Not provided')
            value2 = data_v2.get(field, 'Not provided')

            if isinstance(value1, str) and value1.startswith('['):
                try:
                    value1 = ', '.join(json.loads(value1))
                except json.JSONDecodeError:
                    pass
            if isinstance(value2, str) and value2.startswith('['):
                try:
                    value2 = ', '.join(json.loads(value2))
                except json.JSONDecodeError:
                    pass

            if value1 != value2:
                form_changes.append({
                    'field': displayed_name,
                    'old_value': value1,
                    'new_value': value2
                })

        if form_changes:
            comparison_data.append({
                'form_name': form.name,
                'changes': form_changes
            })

    return render(request, 'submission/compare_versions.html', {
        'submission': submission,
        'version1': version1,
        'version2': version2,
        'comparison_data': comparison_data,
    })

@login_required
def download_submission_pdf(request, submission_id, version=None):
    """Generate and download PDF version of a submission."""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to view this submission.")
            return redirect('submission:dashboard')

        # If version is not specified, use version 1 for new submissions
        if version is None:
            # If submission.version is 2, it means we just submitted version 1
            version = submission.version - 1 if submission.version > 1 else 1
            
        logger.info(f"Generating PDF for submission {submission_id} version {version}")

        # Check if form entries exist for this version
        form_entries = FormDataEntry.objects.filter(
            submission=submission,
            version=version
        )
        
        if not form_entries.exists():
            logger.warning(f"No form entries found for version {version}, checking version 1")
            # Try version 1 as fallback
            version = 1
            form_entries = FormDataEntry.objects.filter(
                submission=submission,
                version=version
            )

        # Generate PDF
        response = generate_submission_pdf(
            submission=submission,
            version=version,
            user=request.user,
            as_buffer=False
        )
        
        if response is None:
            messages.error(request, "Error generating PDF. Please try again later.")
            logger.error(f"PDF generation failed for submission {submission_id} version {version}")
            return redirect('submission:dashboard')
            
        return response

    except Exception as e:
        logger.error(f"Error in download_submission_pdf: {str(e)}")
        logger.error("Error details:", exc_info=True)
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('submission:dashboard')

@login_required
def update_coinvestigator_order(request, submission_id):
    """Update the order of co-investigators in a submission."""
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

@login_required
def user_autocomplete(request):
    term = request.GET.get('term', '').strip()
    submission_id = request.GET.get('submission_id')
    user_type = request.GET.get('user_type')  # 'investigator', 'assistant', or 'coinvestigator'
    
    if len(term) < 2:
        return JsonResponse([], safe=False)

    # Start with base user query
    users = User.objects.filter(
        Q(userprofile__full_name__icontains=term) |
        Q(first_name__icontains=term) |
        Q(last_name__icontains=term) |
        Q(email__icontains=term)
    )

    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        
        # Exclude users already assigned to this submission in any role
        excluded_users = []
        
        # Exclude primary investigator
        if submission.primary_investigator:
            excluded_users.append(submission.primary_investigator.id)
        
        # Exclude research assistants
        assistant_ids = ResearchAssistant.objects.filter(
            submission=submission
        ).values_list('user_id', flat=True)
        excluded_users.extend(assistant_ids)
        
        # Exclude co-investigators
        coinvestigator_ids = CoInvestigator.objects.filter(
            submission=submission
        ).values_list('user_id', flat=True)
        excluded_users.extend(coinvestigator_ids)

        users = users.exclude(id__in=excluded_users)

    users = users.distinct()[:10]

    results = [
        {
            'id': user.id,
            'label': f"{user.userprofile.full_name or user.get_full_name()} ({user.email})"
        }
        for user in users
    ]

    return JsonResponse(results, safe=False)

@login_required
def submission_autocomplete(request):
    """View for handling submission autocomplete requests"""
    term = request.GET.get('term', '')
    user = request.user
    
    # Query submissions that the user has access to
    submissions = Submission.objects.filter(
        Q(primary_investigator=user) |
        Q(coinvestigators__user=user) |
        Q(research_assistants__user=user),
        Q(title__icontains=term) |
        Q(irb_number__icontains=term)
    ).distinct()[:10]

    results = []
    for submission in submissions:
        label = f"{submission.title}"
        if submission.irb_number:
            label += f" (IRB: {submission.irb_number})"
        results.append({
            'id': submission.temporary_id,
            'text': label
        })

    return JsonResponse({'results': results}, safe=False)



