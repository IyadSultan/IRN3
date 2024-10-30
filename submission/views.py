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


@login_required
def edit_submission(request, submission_id):
    return redirect('submission:start_submission_with_id', submission_id=submission_id)


@login_required
def start_submission(request, submission_id=None):
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
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

    if request.method == 'POST':
        django_form_class = generate_django_form(dynamic_form)
        form_instance = django_form_class(request.POST, prefix=f'form_{dynamic_form.id}')

        # Save data without validation
        for field_name in form_instance.fields.keys():
            key = f'form_{dynamic_form.id}-{field_name}'
            value = request.POST.get(key, '').strip()
            FormDataEntry.objects.update_or_create(
                submission=submission,
                form=dynamic_form,
                field_name=field_name,
                defaults={'value': value, 'version': submission.version}
            )
            logger.debug(f"Saved field '{field_name}' with value '{value}' for submission '{submission.temporary_id}'")

        messages.success(request, f'Form "{dynamic_form.name}" saved.')

        # Handle actions
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
        elif action == 'back':
            previous_form = get_previous_form(submission, dynamic_form)
            if previous_form:
                return redirect('submission:submission_form', submission_id=submission.temporary_id, form_id=previous_form.id)
            else:
                return redirect('submission:add_coinvestigator', submission_id=submission.temporary_id)
        elif action == 'save_exit':
            return redirect('submission:dashboard')
        elif action == 'save_continue':
            next_form = get_next_form(submission, dynamic_form)
            if next_form:
                return redirect('submission:submission_form', submission_id=submission.temporary_id, form_id=next_form.id)
            else:
                return redirect('submission:submission_review', submission_id=submission.temporary_id)
    else:
        # GET request
        django_form_class = generate_django_form(dynamic_form)
        initial_data = {
            entry.field_name: entry.value
            for entry in FormDataEntry.objects.filter(
                submission=submission, form=dynamic_form, version=submission.version
            )
        }
        form_instance = django_form_class(initial=initial_data, prefix=f'form_{dynamic_form.id}')

    previous_form = get_previous_form(submission, dynamic_form)
    context = {
        'form': form_instance,
        'submission': submission,
        'dynamic_form': dynamic_form,
        'previous_form': previous_form,
    }
    return render(request, 'submission/dynamic_form.html', context)
# submission/views.py

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
        if not form_instance.is_valid():
            logger.debug(f"Form '{dynamic_form.name}' is invalid: {form_instance.errors}")
            validation_errors[dynamic_form.name] = form_instance.errors
        else:
            logger.debug(f"Form '{dynamic_form.name}' is valid.")

    # Handle document uploads
    documents = submission.documents.all()
    doc_form = DocumentForm()  # Initialize doc_form here

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'submit_final':
            if missing_documents or validation_errors:
                messages.error(
                    request,
                    'Please resolve the missing documents and form errors before final submission.'
                )
            else:
                submission.is_locked = True
                submission.status = 'submitted'
                submission.date_submitted = timezone.now()
                submission.version += 1  # Increment version if applicable
                submission.save()
                # Create version history entry
                VersionHistory.objects.create(
                    submission=submission,
                    version=submission.version,
                    status=submission.status,
                    date=timezone.now(),
                )
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
    if version is None:
        version = submission.version
    else:
        version = int(version)
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="submission_{submission.temporary_id}_v{version}.pdf"'
    # Create the PDF object using ReportLab
    p = canvas.Canvas(response, pagesize=letter)
    # Add content to the PDF
    p.drawString(100, 750, f"Submission ID: {submission.temporary_id}")
    p.drawString(100, 730, f"Title: {submission.title}")
    p.drawString(100, 710, f"Primary Investigator: {submission.primary_investigator.get_full_name()}")
    p.drawString(100, 690, f"Status: {submission.get_status_display()}")
    p.drawString(100, 670, f"Version: {version}")
    # Fetch form data entries for the specified version
    form_entries = FormDataEntry.objects.filter(submission=submission, version=version)
    y = 650
    for entry in form_entries:
        p.drawString(100, y, f"{entry.field_name}: {entry.value}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
    p.showPage()
    p.save()
    return response


@login_required
def compare_versions(request, submission_id, version1, version2):
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')
    data = compare_versions(submission, version1, version2)
    return render(request, 'submission/compare_versions.html', {
        'submission': submission,
        'version1': version1,
        'version2': version2,
        'data': data,
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