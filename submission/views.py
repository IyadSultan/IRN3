# submission/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from forms_builder.models import DynamicForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dal import autocomplete
import json
from django import forms

from .models import Submission, VersionHistory, Document, FormDataEntry
from .forms import DocumentForm
from .utils import (
    has_edit_permission,
    check_researcher_documents,
)

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
    generate_django_form,
    DocumentForm,
)
from .utils import (
    has_edit_permission,
    check_researcher_documents,
    get_next_form,
    get_previous_form,
    compare_versions,
)
from forms_builder.models import DynamicForm
from messaging.models import Message
from .utils import get_system_user  # adjust import path as needed
from users.models import SystemSettings


@login_required
def edit_submission(request, submission_id):
    return redirect('submission:start_submission_with_id', submission_id=submission_id)


@login_required
def start_submission(request, submission_id=None):
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to edit this submission.")
            return redirect('submission:dashboard')
    else:
        submission = None

    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
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
                    return render(request, 'submission/start_submission.html', {'form': form, 'submission': submission})
            submission.save()
            messages.success(request, f'Temporary submission ID {submission.temporary_id} generated.')
            # Handle different actions
            if action == 'save_exit':
                return redirect('submission:dashboard')
            elif action == 'save_continue':
                return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
        else:
            messages.error(request, 'Please correct the errors below.')
            validation_errors = form.errors  # Capture validation errors

    else:
        form = SubmissionForm(instance=submission)
        validation_errors = {}

    return render(request, 'submission/start_submission.html', {
        'form': form,
        'submission': submission,
        'validation_errors': validation_errors,  # Pass validation errors to the template
    })


@login_required
def add_research_assistant(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        # Handle delete action
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

        # Handle navigation without validation
        if action == 'back':
            return redirect('submission:start_submission', submission_id=submission.temporary_id)

        if action == 'exit_no_save':
            return redirect('submission:dashboard')

        if action == 'save_continue':
            return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)

        # Validate and save data
        if action in ['save_exit', 'save_add_another']:
            form = ResearchAssistantForm(request.POST)
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
                else:
                    messages.error(request, 'Please select a research assistant.')

                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please correct the errors below.')

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
    submission = get_object_or_404(Submission, pk=submission_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Handle delete action
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

        # Handle navigation without validation
        if action == 'back':
            return redirect('submission:add_research_assistant', submission_id=submission.temporary_id)

        if action == 'exit_no_save':
            return redirect('submission:dashboard')

        if action == 'save_continue':
            # Redirect to the first dynamic form
            first_form = submission.study_type.forms.order_by('order').first()
            if first_form:
                return redirect('submission:submission_form', submission_id=submission.temporary_id, form_id=first_form.id)
            else:
                return redirect('submission:submission_review', submission_id=submission.temporary_id)

        # Validate and save data
        if action in ['save_exit', 'save_add_another']:
            form = CoInvestigatorForm(request.POST)
            if form.is_valid():
                investigator = form.cleaned_data.get('investigator')
                role_in_study = form.cleaned_data.get('role_in_study')
                if investigator and role_in_study:
                    CoInvestigator.objects.create(
                        submission=submission,
                        user=investigator,
                        role_in_study=role_in_study,
                        can_submit=form.cleaned_data.get('can_submit', False),
                        can_edit=form.cleaned_data.get('can_edit', False),
                        can_view_communications=form.cleaned_data.get('can_view_communications', False)
                    )
                    messages.success(request, 'Co-investigator added successfully.')
                else:
                    messages.error(request, 'Please select a co-investigator and specify their role.')

                if action == 'save_exit':
                    return redirect('submission:dashboard')
                elif action == 'save_add_another':
                    return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
            else:
                messages.error(request, 'Please correct the errors below.')

    else:
        form = CoInvestigatorForm()

    coinvestigators = CoInvestigator.objects.filter(submission=submission)
    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'submission': submission,
        'coinvestigators': coinvestigators
    })


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


# submission/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dal import autocomplete
import json

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
    compare_versions,
)
from forms_builder.models import DynamicForm
from messaging.models import Message
from users.models import UserProfile  # Ensure UserProfile is imported if needed

@login_required
def dashboard(request):
    submissions = Submission.objects.filter(
        primary_investigator=request.user
    ).select_related('study_type')
    return render(request, 'submission/dashboard.html', {'submissions': submissions})

import logging

logger = logging.getLogger(__name__)

@login_required
def submission_form(request, submission_id, form_id):
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')
    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    dynamic_form = get_object_or_404(DynamicForm, pk=form_id)
    action = request.POST.get('action')

    def safe_json_loads(value):
        """Safely convert JSON string to Python object"""
        try:
            if isinstance(value, str) and value.startswith('['):
                return json.loads(value)
            return value
        except json.JSONDecodeError:
            return value

    # Get previous version's data
    previous_version_data = None
    if submission.version > 1:
        previous_version_data = FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version - 1
        ).values('field_name', 'value')
        # Safely convert values
        previous_version_data = {
            entry['field_name']: safe_json_loads(entry['value'])
            for entry in previous_version_data
        }

    if request.method == 'POST':
        # Get the form class
        DynamicFormClass = generate_django_form(dynamic_form)
        form_instance = DynamicFormClass(request.POST, prefix=f'form_{dynamic_form.id}')
        
        if action == 'back':
            previous_form = get_previous_form(submission, dynamic_form)
            if previous_form:
                return redirect('submission:submission_form', 
                              submission_id=submission.temporary_id, 
                              form_id=previous_form.id)
            return redirect('submission:add_coinvestigator', 
                          submission_id=submission.temporary_id)
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
        
        if form_instance.is_valid():
            # Save form data
            for field_name, value in form_instance.cleaned_data.items():
                # Convert lists to JSON strings for storage
                if isinstance(value, (list, tuple)):
                    value = json.dumps(value)
                    print(f"Saving checkbox field {field_name} with value: {value}")  # Debug line
                FormDataEntry.objects.update_or_create(
                    submission=submission,
                    form=dynamic_form,
                    field_name=field_name,
                    version=submission.version,
                    defaults={'value': value}
                )
            
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
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Get the form class
        DynamicFormClass = generate_django_form(dynamic_form)
        
        # Get current version's data
        current_data = FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version
        ).values('field_name', 'value')
        
        # Convert values and handle checkboxes specifically
        current_data = {}
        for entry in FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version
        ):
            if isinstance(DynamicFormClass.base_fields.get(entry.field_name), forms.MultipleChoiceField):
                try:
                    current_data[entry.field_name] = json.loads(entry.value)
                except (json.JSONDecodeError, TypeError):
                    current_data[entry.field_name] = []
            else:
                current_data[entry.field_name] = entry.value

        # Get previous version's data if needed
        if not current_data and submission.version > 1 and not submission.is_locked:
            previous_data = {}
            for entry in FormDataEntry.objects.filter(
                submission=submission,
                form=dynamic_form,
                version=submission.version - 1
            ):
                if isinstance(DynamicFormClass.base_fields.get(entry.field_name), forms.MultipleChoiceField):
                    try:
                        previous_data[entry.field_name] = json.loads(entry.value)
                    except (json.JSONDecodeError, TypeError):
                        previous_data[entry.field_name] = []
                else:
                    previous_data[entry.field_name] = entry.value
            initial_data = previous_data
        else:
            initial_data = current_data

        # Create form instance with initial data
        form_instance = DynamicFormClass(
            initial=initial_data, 
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
    submission = get_object_or_404(Submission, temporary_id=submission_id)

    if submission.is_locked and not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to edit this submission.")
        return redirect('submission:dashboard')

    # Check documents for all researchers
    missing_documents = check_researcher_documents(submission)

    # Perform form data validation
    validation_errors = {}
    dynamic_forms = submission.study_type.forms.order_by('order')
    for dynamic_form in dynamic_forms:
        django_form_class = generate_django_form(dynamic_form)
        # Get saved data
        entries = FormDataEntry.objects.filter(
            submission=submission, form=dynamic_form, version=submission.version
        )
        saved_data = {
            f'form_{dynamic_form.id}-{entry.field_name}': entry.value
            for entry in entries
        }
        logger.debug(f"Validating form '{dynamic_form.name}' with data: {saved_data}")
        form_instance = django_form_class(data=saved_data, prefix=f'form_{dynamic_form.id}')
        
        # Custom validation for MultipleChoiceFields
        is_valid = True
        errors = {}
        for field_name, field in form_instance.fields.items():
            if isinstance(field, forms.MultipleChoiceField):
                field_key = f'form_{dynamic_form.id}-{field_name}'
                field_value = saved_data.get(field_key)
                if not field_value:  # No option selected
                    is_valid = False
                    errors[field_name] = ['Please select at least one option']
            else:
                field_value = form_instance.data.get(f'form_{dynamic_form.id}-{field_name}')
                if field.required and not field_value:
                    is_valid = False
                    errors[field_name] = ['This field is required']

        if not is_valid:
            logger.debug(f"Form '{dynamic_form.name}' is invalid: {errors}")
            validation_errors[dynamic_form.name] = errors
        else:
            logger.debug(f"Form '{dynamic_form.name}' is valid.")

    # Handle document uploads
    documents = submission.documents.all()
    doc_form = DocumentForm()  # Initialize doc_form here

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'submit_final':
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
            else:
                submission.is_locked = True
                submission.status = 'submitted'
                submission.date_submitted = timezone.now()
                submission.version += 1
                submission.save()
                
                # Create version history entry
                VersionHistory.objects.create(
                    submission=submission,
                    version=submission.version,
                    status=submission.status,
                    date=timezone.now(),
                )

                # Create notification message using the configured system user
                message = Message.objects.create(
                    sender=SystemSettings.get_system_user(),
                    subject=f"Submission {submission.temporary_id} Successfully Submitted",
                    body=f"""Your submission "{submission.title}" (ID: {submission.temporary_id}) has been successfully submitted.
                    
                    Date Submitted: {submission.date_submitted.strftime('%Y-%m-%d %H:%M')}
                    Version: {submission.version}
                    
                    You will be notified when there are any updates regarding your submission.
                    
                    Best regards,
                    AIDI Office""",
                    study_name=submission.title,
                )
                
                # Set the recipients after creating the message
                message.recipients.set([submission.primary_investigator])

                messages.success(request, 'Submission has been finalized and locked.')
                return redirect('submission:dashboard')
        elif action == 'back':
            # Redirect to the last dynamic form
            last_form = submission.study_type.forms.order_by('-order').first()
            if last_form:
                return redirect(
                    'submission:submission_form',
                    submission_id=submission.temporary_id,
                    form_id=last_form.id
                )
            else:
                return redirect(
                    'submission:add_coinvestigator',
                    submission_id=submission.temporary_id
                )
        elif action == 'exit_no_save':
            return redirect('submission:dashboard')
        elif action == 'upload_document':
            doc_form = DocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                document = doc_form.save(commit=False)
                document.submission = submission
                document.uploaded_by = request.user
                # Check file extension
                ext = document.file.name.split('.')[-1].lower()
                if ext in Document.ALLOWED_EXTENSIONS:
                    document.save()
                    messages.success(request, 'Document uploaded successfully.')
                    return redirect('submission:submission_review', submission_id=submission_id)
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
    submission = get_object_or_404(Submission, pk=submission_id)
    histories = submission.version_histories.order_by('-version')
    return render(request, 'submission/version_history.html', {
        'submission': submission,
        'histories': histories,
    })


@login_required
def download_submission_pdf(request, submission_id, version=None):
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # If version is not specified, use the latest version
    if version is None:
        version = submission.version

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="submission_{submission.temporary_id}_v{version}.pdf"'

    # Create the PDF object using ReportLab
    p = canvas.Canvas(response, pagesize=letter)
    y = 750  # Starting y position
    line_height = 20  # Space between lines

    def add_header(canvas_page, y_position):
        """Add header to each page"""
        canvas_page.setFont("Helvetica-Bold", 16)
        canvas_page.drawString(100, y_position, "intelligent Research Navigator (iRN) report")
        y_position -= line_height * 1.5
        
        canvas_page.setFont("Helvetica-Bold", 14)
        canvas_page.drawString(100, y_position, f"{submission.title} - Version {version}")
        y_position -= line_height * 1.5
        
        canvas_page.setFont("Helvetica", 10)
        canvas_page.drawString(100, y_position, f"Date of printing: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        y_position -= line_height
        canvas_page.drawString(100, y_position, f"Printed by: {request.user.get_full_name()}")
        
        return y_position - (line_height * 2)  # Return new y position after header

    def add_footer(canvas_page):
        """Add footer to each page"""
        footer_text = (
            "iRN is a property of the Artificial Intelligence and Data Innovation (AIDI) office "
            "in collaboration with the Office of Scientific Affairs (OSAR) office @ King Hussein "
            "Cancer Center, Amman - Jordan. Keep this document confidential."
        )
        canvas_page.setFont("Helvetica", 8)
        text_object = canvas_page.beginText()
        text_object.setTextOrigin(100, 50)
        
        # Word wrap the footer text
        words = footer_text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= 90:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        for line in lines:
            text_object.textLine(line)
        
        canvas_page.drawText(text_object)

    # Add header to first page
    y = add_header(p, y)

    # Add basic submission details
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Basic Information")
    y -= line_height

    p.setFont("Helvetica", 10)
    basic_info = [
        f"Submission ID: {submission.temporary_id}",
        f"Study Type: {submission.study_type}",
        f"IRB Number: {submission.irb_number or 'Not provided'}",
        f"Status: {submission.get_status_display()}",
        f"Date Created: {submission.date_created.strftime('%Y-%m-%d')}",
        f"Date Submitted: {submission.date_submitted.strftime('%Y-%m-%d') if submission.date_submitted else 'Not submitted'}",
    ]

    for info in basic_info:
        p.drawString(100, y, info)
        y -= line_height

    # Add Research Team section
    y -= line_height
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Research Team")
    y -= line_height

    p.setFont("Helvetica", 10)
    p.drawString(100, y, f"Primary Investigator: {submission.primary_investigator.get_full_name()}")
    y -= line_height

    # Add Co-Investigators
    coinvestigators = submission.coinvestigators.all()
    if coinvestigators:
        y -= line_height/2
        p.drawString(100, y, "Co-Investigators:")
        y -= line_height
        for ci in coinvestigators:
            p.drawString(120, y, f"- {ci.user.get_full_name()} (Role: {ci.role_in_study})")
            y -= line_height

    # Add Research Assistants
    research_assistants = submission.research_assistants.all()
    if research_assistants:
        y -= line_height/2
        p.drawString(100, y, "Research Assistants:")
        y -= line_height
        for ra in research_assistants:
            p.drawString(120, y, f"- {ra.user.get_full_name()}")
            y -= line_height

    # Add form data for each dynamic form
    for dynamic_form in submission.study_type.forms.all():
        # Check if we need a new page
        if y < 100:
            add_footer(p)
            p.showPage()
            y = add_header(p, 750)

        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y, dynamic_form.name)
        y -= line_height * 1.5

        # Get field definitions for displayed names
        field_definitions = {
            field.name: field.displayed_name 
            for field in dynamic_form.fields.all()
        }

        form_entries = FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=version
        )

        p.setFont("Helvetica", 10)
        for entry in form_entries:
            # Check if we need a new page
            if y < 100:
                add_footer(p)
                p.showPage()
                y = add_header(p, 750)
                p.setFont("Helvetica", 10)

            displayed_name = field_definitions.get(entry.field_name, entry.field_name)
            
            # Handle checkbox/list values
            if entry.value.startswith('['):
                try:
                    value_list = json.loads(entry.value)
                    value_str = ", ".join(value_list)
                except json.JSONDecodeError:
                    value_str = entry.value
            else:
                value_str = entry.value

            # Word wrap for long values
            if len(str(value_str)) > 60:
                words = str(value_str).split()
                lines = []
                current_line = []
                current_length = 0

                for word in words:
                    if current_length + len(word) + 1 <= 60:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_length = len(word)

                if current_line:
                    lines.append(" ".join(current_line))

                p.drawString(100, y, f"{displayed_name}:")
                y -= line_height
                for line in lines:
                    p.drawString(120, y, line)
                    y -= line_height
            else:
                p.drawString(100, y, f"{displayed_name}: {value_str}")
                y -= line_height

        y -= line_height  # Extra space between forms

    # Add attached documents list
    if y < 100:
        add_footer(p)
        p.showPage()
        y = add_header(p, 750)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Attached Documents")
    y -= line_height

    p.setFont("Helvetica", 10)
    documents = submission.documents.all()
    if documents:
        for doc in documents:
            p.drawString(100, y, f"- {doc.file.name.split('/')[-1]} (Uploaded by: {doc.uploaded_by.get_full_name()})")
            y -= line_height
    else:
        p.drawString(100, y, "No documents attached")

    # Add footer to the last page
    add_footer(p)
    p.showPage()
    p.save()
    return response


@login_required
def compare_versions(request, submission_id, version1, version2):
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # Get all forms for this submission's study type
    forms = submission.study_type.forms.all()
    
    comparison_data = []
    
    for form in forms:
        # Get entries for both versions
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

        # Create dictionaries for easy comparison
        data_v1 = {entry.field_name: entry.value for entry in entries_v1}
        data_v2 = {entry.field_name: entry.value for entry in entries_v2}

        # Get field definitions for displayed names
        field_definitions = {
            field.name: field.displayed_name 
            for field in form.fields.all()
        }

        # Compare fields
        form_changes = []
        all_fields = set(data_v1.keys()) | set(data_v2.keys())
        
        for field in all_fields:
            displayed_name = field_definitions.get(field, field)
            value1 = data_v1.get(field, 'Not provided')
            value2 = data_v2.get(field, 'Not provided')

            # Handle checkbox/list values
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
def dashboard(request):
    submissions = Submission.objects.filter(
        primary_investigator=request.user
    ).select_related('study_type')
    return render(request, 'submission/dashboard.html', {'submissions': submissions})


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()  # Return empty queryset if not authenticated

        qs = User.objects.all()

        if self.q:
            qs = qs.filter(username__icontains=self.q)

        return qs