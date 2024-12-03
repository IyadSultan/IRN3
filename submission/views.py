from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from django.db import transaction
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from dal import autocomplete
import json
from io import BytesIO
import logging

from .models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
    InvestigatorFormSubmission,
    PermissionChangeLog,
    StudyAction,
    StudyActionDocument,
)

from .forms import (
    SubmissionForm,
    ResearchAssistantForm,
    CoInvestigatorForm,
    DocumentForm,
    generate_django_form,
)
from forms_builder.models import DynamicForm
from messaging.models import Message, MessageAttachment
from users.models import SystemSettings, UserProfile
from .utils import (
    PDFGenerator, 
    has_edit_permission, 
    check_researcher_documents, 
    get_next_form, 
    get_previous_form
)
from .utils.pdf_generator import generate_submission_pdf
from .gpt_analysis import ResearchAnalyzer
from django.core.cache import cache
from .utils.permissions import check_submission_permission
from django.db.models import Q

logger = logging.getLogger(__name__)
def get_system_user():
    """Get or create the system user for automated messages."""
    try:
        with transaction.atomic():
            # First try to get existing system user
            try:
                system_user = User.objects.get(username='system')
            except User.DoesNotExist:
                # Create new system user if doesn't exist
                system_user = User.objects.create(
                    username='system',
                    email=SystemSettings.get_system_email(),
                    first_name='System',
                    last_name='User',
                    is_active=True
                )
            
            # Try to get or create UserProfile
            try:
                profile = UserProfile.objects.get(user=system_user)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(
                    user=system_user,
                    full_name='System User',
                    phone_number='',
                    department='',
                    position='System'
                )
            
            return system_user
            
    except Exception as e:
        logger.error(f"Error in get_system_user: {str(e)}")
        logger.error("Error details:", exc_info=True)
        
        # Final fallback - just get or create the user without profile
        try:
            system_user = User.objects.get(username='system')
        except User.DoesNotExist:
            system_user = User.objects.create(
                username='system',
                email='aidi@khcc.jo',
                first_name='System',
                last_name='User',
                is_active=True
            )
        return system_user

@login_required
def dashboard(request):
    """Display user's submissions dashboard."""
    from django.db.models import Max, Prefetch
    
    # Get all active submissions for the user
    submissions = Submission.objects.filter(
        is_archived=False
    ).select_related(
        'primary_investigator__userprofile',
        'study_type'
    ).prefetch_related(
        'coinvestigators',
        'research_assistants'
    ).order_by('-date_created')
    
    # Process each submission
    for submission in submissions:
        # Get actual latest version
        latest_version = FormDataEntry.objects.filter(
            submission=submission
        ).values('version').aggregate(Max('version'))['version__max']
        submission.actual_version = latest_version or 1
        
        # Check for pending forms
        submission.has_pending = submission.has_pending_forms(request.user)
        
        # Get required forms for this user
        submission.pending_forms = submission.get_pending_investigator_forms(request.user)

    return render(request, 'submission/dashboard.html', {
        'submissions': submissions
    })
@login_required
def edit_submission(request, submission_id):
    """Redirect to start_submission with existing submission ID."""
    return redirect('submission:start_submission_with_id', submission_id=submission_id)

@login_required
def start_submission(request, submission_id=None):
    """Start or edit a submission."""
    if submission_id:
        submission = get_object_or_404(Submission, pk=submission_id)
        if submission.is_locked:
            messages.error(request, "This submission is locked and cannot be edited.")
            return redirect('submission:dashboard')
        if not has_edit_permission(request.user, submission):
            messages.error(request, "You do not have permission to edit this submission.")
            return redirect('submission:dashboard')
        
        initial_data = {
            'primary_investigator': submission.primary_investigator
        }
    else:
        submission = None
        initial_data = {}

    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        action = request.POST.get('action')
        
        if action == 'exit_no_save':
            return redirect('submission:dashboard')
            
        if form.is_valid():
            try:
                with transaction.atomic():
                    submission = form.save(commit=False)
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

                    # Save the submission first
                    submission.save()
                    form.save_m2m()

                    # Handle user role if not PI
                    if request.user != submission.primary_investigator:
                        user_role = request.POST.get('user_role')
                        
                        if user_role == 'research_assistant':
                            ResearchAssistant.objects.create(
                                submission=submission,
                                user=request.user,
                                can_edit=True,
                                can_submit=True,
                                can_view_communications=True
                            )
                        elif user_role == 'coinvestigator':
                            # Get selected roles
                            ci_roles = request.POST.getlist('ci_roles')
                            if not ci_roles:
                                ci_roles = ['general']  # Default role if none selected
                                
                            CoInvestigator.objects.create(
                                submission=submission,
                                user=request.user,
                                can_edit=True,
                                can_submit=True,
                                can_view_communications=True,
                                roles=ci_roles
                            )
                        else:
                            messages.error(request, 'Please select your role in the submission.')
                            return render(request, 'submission/start_submission.html', {
                                'form': form,
                                'submission': submission
                            })

                    messages.success(request, 'Submission saved successfully.')
                    
                    if action == 'save_exit':
                        return redirect('submission:dashboard')
                    elif action == 'save_continue':
                        return redirect('submission:add_research_assistant', 
                                     submission_id=submission.temporary_id)

            except Exception as e:
                logger.error(f"Error in start_submission: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'submission/start_submission.html', {
                    'form': form,
                    'submission': submission
                })
    else:
        form = SubmissionForm(instance=submission, initial=initial_data)
        if submission and submission.primary_investigator == request.user:
            form.fields['is_primary_investigator'].initial = True

    return render(request, 'submission/start_submission.html', {
        'form': form,
        'submission': submission
    })



@login_required
def add_research_assistant(request, submission_id):
    """Add or manage research assistants for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check if user has permission to modify research assistants
    if not submission.can_user_edit(request.user):
        messages.error(request, "You don't have permission to modify research assistants.")
        return redirect('submission:dashboard')

    if submission.is_locked:
        messages.error(request, "This submission is locked and cannot be edited.")
        return redirect('submission:dashboard')

    # Initialize form variable
    form = ResearchAssistantForm(submission=submission)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_assistant':
            assistant_id = request.POST.get('assistant_id')
            if assistant_id:
                try:
                    assistant = ResearchAssistant.objects.get(id=assistant_id, submission=submission)
                    # Log the deletion
                    PermissionChangeLog.objects.create(
                        submission=submission,
                        user=assistant.user,
                        changed_by=request.user,
                        permission_type='removed',
                        old_value=True,
                        new_value=False,
                        role='research_assistant',
                        notes=f"Research Assistant removed from submission by {request.user.get_full_name()}"
                    )
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
                try:
                    with transaction.atomic():
                        # Create new research assistant
                        ra = ResearchAssistant(
                            submission=submission,
                            user=assistant,
                            can_submit=form.cleaned_data.get('can_submit', False),
                            can_edit=form.cleaned_data.get('can_edit', False),
                            can_view_communications=form.cleaned_data.get('can_view_communications', False)
                        )
                        
                        # Save first
                        ra.save()
                        
                        # Then log permission changes
                        ra.log_permission_changes(changed_by=request.user, is_new=True)

                        # Create notification
                        Message.objects.create(
                            sender=get_system_user(),
                            subject=f'Added as Research Assistant to {submission.title}',
                            body=f"""
You have been added as a Research Assistant to:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Principal Investigator: {submission.primary_investigator.get_full_name()}

Your permissions:
- Can Edit: {'Yes' if ra.can_edit else 'No'}
- Can Submit: {'Yes' if ra.can_submit else 'No'}
- Can View Communications: {'Yes' if ra.can_view_communications else 'No'}

Please log in to view the submission.
                            """.strip(),
                            related_submission=submission
                        ).recipients.add(assistant)

                        messages.success(request, 'Research assistant added successfully.')
                        
                        if action == 'save_exit':
                            return redirect('submission:dashboard')
                        elif action == 'save_add_another':
                            return redirect('submission:add_research_assistant', 
                                         submission_id=submission.temporary_id)

                except IntegrityError:
                    messages.error(request, 'This user is already a research assistant for this submission.')
                except Exception as e:
                    logger.error(f"Error saving research assistant: {str(e)}")
                    messages.error(request, f'Error adding research assistant: {str(e)}')

    # Get research assistants with permission information
    assistants = ResearchAssistant.objects.filter(submission=submission).select_related('user')
    
    # Get permission change history
    permission_history = PermissionChangeLog.objects.filter(
        submission=submission,
        role='research_assistant'
    ).select_related('user', 'changed_by').order_by('-change_date')[:10]

    return render(request, 'submission/add_research_assistant.html', {
        'form': form,
        'submission': submission,
        'assistants': assistants,
        'permission_history': permission_history,
        'can_modify': submission.can_user_edit(request.user)
    })

@login_required
def add_coinvestigator(request, submission_id):
    """Add or manage co-investigators for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check if user has permission to modify co-investigators
    if not submission.can_user_edit(request.user):
        messages.error(request, "You don't have permission to modify co-investigators.")
        return redirect('submission:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_coinvestigator':
            coinvestigator_id = request.POST.get('coinvestigator_id')
            if coinvestigator_id:
                try:
                    coinvestigator = CoInvestigator.objects.get(id=coinvestigator_id, submission=submission)
                    # Log the deletion
                    PermissionChangeLog.objects.create(
                        submission=submission,
                        user=coinvestigator.user,
                        changed_by=request.user,
                        permission_type='removed',
                        old_value=True,
                        new_value=False,
                        role='co_investigator',
                        notes=f"Co-investigator removed from submission by {request.user.get_full_name()}"
                    )
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
                try:
                    with transaction.atomic():
                        # Create new co-investigator
                        coinv = CoInvestigator(
                            submission=submission,
                            user=investigator,
                            can_submit=form.cleaned_data.get('can_submit', False),
                            can_edit=form.cleaned_data.get('can_edit', False),
                            can_view_communications=form.cleaned_data.get('can_view_communications', False)
                        )
                        
                        # Set roles (it's a list field, not M2M)
                        coinv.roles = list(selected_roles)
                        
                        # Save first
                        coinv.save()
                        
                        # Then log permission changes
                        coinv.log_permission_changes(changed_by=request.user, is_new=True)

                        # Create notification
                        Message.objects.create(
                            sender=get_system_user(),
                            subject=f'Added as Co-Investigator to {submission.title}',
                            body=f"""
You have been added as a Co-Investigator to:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Principal Investigator: {submission.primary_investigator.get_full_name()}

Your roles: {', '.join(coinv.get_role_display())}

Your permissions:
- Can Edit: {'Yes' if coinv.can_edit else 'No'}
- Can Submit: {'Yes' if coinv.can_submit else 'No'}
- Can View Communications: {'Yes' if coinv.can_view_communications else 'No'}

Please log in to view the submission.
                            """.strip(),
                            related_submission=submission
                        ).recipients.add(investigator)

                        messages.success(request, 'Co-investigator added successfully.')
                        
                        if action == 'save_exit':
                            return redirect('submission:dashboard')
                        elif action == 'save_add_another':
                            return redirect('submission:add_coinvestigator', 
                                         submission_id=submission.temporary_id)

                except IntegrityError:
                    messages.error(request, 'This user is already a co-investigator for this submission.')
                except Exception as e:
                    logger.error(f"Error saving co-investigator: {str(e)}")
                    messages.error(request, f'Error adding co-investigator: {str(e)}')
            else:
                messages.error(request, 'Please select a co-investigator.')
    else:
        form = CoInvestigatorForm()

    coinvestigators = CoInvestigator.objects.filter(submission=submission)
    
    # Get permission change history
    permission_history = PermissionChangeLog.objects.filter(
        submission=submission,
        role='co_investigator'
    ).select_related('user', 'changed_by').order_by('-change_date')[:10]

    return render(request, 'submission/add_coinvestigator.html', {
        'form': form,
        'submission': submission,
        'coinvestigators': coinvestigators,
        'permission_history': permission_history,
        'can_modify': submission.can_user_edit(request.user)
    })


@login_required
@check_submission_permission('edit')
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
    previous_form = get_previous_form(submission, dynamic_form)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Handle navigation actions without form processing
        if action in ['back', 'exit_no_save']:
            if action == 'back':
                if previous_form:
                    return redirect('submission:submission_form', 
                                  submission_id=submission.temporary_id, 
                                  form_id=previous_form.id)
                return redirect('submission:add_coinvestigator', 
                              submission_id=submission.temporary_id)
            return redirect('submission:dashboard')

        # Create form instance
        DynamicFormClass = generate_django_form(dynamic_form)
        
        # Save form fields
        for field in dynamic_form.fields.all():
            field_name = field.name
            
            # Handle checkbox fields differently
            if field.field_type == 'checkbox':
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
    entries = FormDataEntry.objects.filter(
        submission=submission,
        form=dynamic_form,
        version=submission.version
    )
    
    for entry in entries:
        field = dynamic_form.fields.get(name=entry.field_name)
        if field:
            if field.field_type == 'checkbox':
                try:
                    current_data[entry.field_name] = json.loads(entry.value)
                except json.JSONDecodeError:
                    current_data[entry.field_name] = []
            else:
                current_data[entry.field_name] = entry.value

    # If no current data and not version 1, get previous version's data
    if not current_data and submission.version > 1 and not submission.is_locked:
        previous_entries = FormDataEntry.objects.filter(
            submission=submission,
            form=dynamic_form,
            version=submission.version - 1
        )
        
        for entry in previous_entries:
            field = dynamic_form.fields.get(name=entry.field_name)
            if field:
                if field.field_type == 'checkbox':
                    try:
                        current_data[entry.field_name] = json.loads(entry.value)
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
        'previous_form': previous_form,
    }
    return render(request, 'submission/dynamic_form.html', context)


@login_required
@check_submission_permission('submit')
def submission_review(request, submission_id):
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    
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
            # Check for required certificates
            missing_certs = check_researcher_documents(submission)
            if missing_certs:
                messages.error(request, 'Cannot submit: All team members must have valid certificates uploaded in the system.')
                return redirect('submission:submission_review', submission_id=submission_id)
            
            # Check for missing documents or validation errors
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
                return redirect('submission:submission_review', submission_id=submission_id)

            try:
                with transaction.atomic():
                    # Submit the submission and track who submitted it
                    submission.submitted_by = request.user
                    submission.date_submitted = timezone.now()
                    submission.is_locked = True

                    # Check for pending forms from non-submitter team members
                    non_submitters = submission.get_non_submitters()
                    required_forms = submission.get_required_investigator_forms()
                    
                    has_pending_forms = False
                    for member in non_submitters:
                        for form in required_forms:
                            if not submission.has_submitted_form(member, form):
                                has_pending_forms = True
                                break
                        if has_pending_forms:
                            break

                    # Set appropriate status
                    submission.status = 'document_missing' if has_pending_forms else 'submitted'
                    submission.save()
                    
                    # Create version history entry with submitter info
                    VersionHistory.objects.create(
                        submission=submission,
                        version=submission.version,
                        status=submission.status,
                        date=timezone.now(),
                        submitted_by=request.user
                    )

                    # Generate submission PDF
                    buffer = generate_submission_pdf(
                        submission=submission,
                        version=submission.version,
                        user=request.user,
                        as_buffer=True
                    )

                    if not buffer:
                        raise ValueError("Failed to generate PDF for submission")

                    # Get system user for notifications
                    system_user = get_system_user()
                    pdf_filename = f"submission_{submission.temporary_id}_v{submission.version}.pdf"

                    # Send notification to PI
                    pi_message = Message.objects.create(
                        sender=system_user,
                        subject=f'Submission {submission.temporary_id} - Version {submission.version} {"Awaiting Forms" if has_pending_forms else "Confirmation"}',
                        body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

Your submission (ID: {submission.temporary_id}) has been submitted by {request.user.get_full_name()}.

Status: {'Pending team member forms' if has_pending_forms else 'Complete submission'}

{'''Some team members still need to complete their required forms.
The submission will be forwarded for review once all forms are completed.''' if has_pending_forms else 'All forms are complete. Your submission will now be reviewed by OSAR.'}

Please find the attached PDF for your records.

Best regards,
AIDI System
                        """.strip(),
                        related_submission=submission
                    )
                    pi_message.recipients.add(submission.primary_investigator)
                    
                    # Attach PDF to PI message
                    pi_attachment = MessageAttachment(message=pi_message)
                    pi_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                    if has_pending_forms:
                        # Notify team members about pending forms
                        notify_pending_forms(submission)
                    else:
                        # Notify OSAR only if all forms are complete
                        notify_osar_of_completion(submission)

                    # Increment version after everything is done
                    submission.version += 1
                    submission.save()

                    messages.success(
                        request, 
                        'Submission completed.' + 
                        (' Awaiting required forms from team members.' if has_pending_forms else ' Sent to OSAR for review.')
                    )
                    return redirect('submission:dashboard')

            except Exception as e:
                logger.error(f"Error in submission finalization: {str(e)}")
                messages.error(request, f"Error during submission: {str(e)}")
                return redirect('submission:dashboard')

        elif action == 'back':
                logger.error(f"Error in submission finalization: {str(e)}")
                messages.error(request, f"Error during submission: {str(e)}")
                return redirect('submission:dashboard')    
        if request.method == 'POST':
            action = request.POST.get('action')
            
        if action == 'submit_final':
            missing_certs = check_researcher_documents(submission)
            if missing_certs:
                messages.error(request, 'Cannot submit: All team members must have valid certificates uploaded in the system.')
                return redirect('submission:submission_review', submission_id=submission_id)
            
            if missing_documents or validation_errors:
                messages.error(request, 'Please resolve the missing documents and form errors before final submission.')
            else:
                try:
                    with transaction.atomic():
                        # Check for required investigator forms
                        required_forms = submission.study_type.forms.filter(requested_per_investigator=True)
                        team_members = []
                        team_members.extend([ci.user for ci in submission.coinvestigators.all()])
                        team_members.extend([ra.user for ra in submission.research_assistants.all()])
                        
                        # Check if there are pending forms for any team member
                        has_pending_forms = False
                        for member in team_members:
                            for form in required_forms:
                                if not InvestigatorFormSubmission.objects.filter(
                                    submission=submission,
                                    form=form,
                                    investigator=member,
                                    version=submission.version
                                ).exists():
                                    has_pending_forms = True
                                    break
                            if has_pending_forms:
                                break

                        # Set status based on pending forms
                        submission.is_locked = True
                        submission.status = 'document_missing' if has_pending_forms else 'submitted'
                        submission.date_submitted = timezone.now()
                        
                        # Create version history entry
                        VersionHistory.objects.create(
                            submission=submission,
                            version=submission.version,
                            status=submission.status,
                            date=timezone.now()
                        )

                        # Generate PDF
                        buffer = generate_submission_pdf(
                            submission=submission,
                            version=submission.version,
                            user=request.user,
                            as_buffer=True
                        )

                        if not buffer:
                            raise ValueError("Failed to generate PDF for submission")

                        # Get system user for automated messages
                        system_user = get_system_user()
                        
                        # Create PDF filename
                        pdf_filename = f"submission_{submission.temporary_id}_v{submission.version}.pdf"

                        # Send confirmation to PI with appropriate message
                        pi_message = Message.objects.create(
                            sender=system_user,
                            subject=f'Submission {submission.temporary_id} - Version {submission.version} {"Awaiting Forms" if has_pending_forms else "Confirmation"}',
                            body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

Your submission (ID: {submission.temporary_id}) has been successfully received.
{'Note: The submission is pending required forms from team members.' if has_pending_forms else 'All required forms have been completed.'}

{'The submission will be forwarded for review once all team members complete their required forms.' if has_pending_forms else 'Your submission will now be reviewed by OSAR.'}

Please find the attached PDF for your records.

Best regards,
AIDI System
                            """.strip(),
                            related_submission=submission
                        )
                        pi_message.recipients.add(submission.primary_investigator)
                        
                        # Attach PDF to PI message
                        pi_attachment = MessageAttachment(message=pi_message)
                        pi_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))

                        if has_pending_forms:
                            # Notify team members about pending forms
                            notify_pending_forms(submission)
                        else:
                            # Notify OSAR only if all forms are complete
                            notify_osar_of_completion(submission)

                        # Increment version after everything is done
                        submission.version += 1
                        submission.save()

                        messages.success(
                            request, 
                            'Submission completed.' + 
                            (' Awaiting required forms from team members.' if has_pending_forms else ' Sent to OSAR for review.')
                        )
                        return redirect('submission:dashboard')

                except Exception as e:
                    logger.error(f"Error in submission finalization: {str(e)}")
                    messages.error(request, f"Error during submission: {str(e)}")
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
        'gpt_analysis': cache.get(f'gpt_analysis_{submission.temporary_id}_{submission.version}'),
        'can_submit': submission.can_user_submit(request.user),
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
    
    if not submission.can_user_view(request.user):
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('submission:dashboard')

    # Get all versions from version history
    histories = VersionHistory.objects.filter(
        submission=submission
    ).order_by('-version')
    
    # Check for pending forms for this user
    pending_forms = submission.get_pending_investigator_forms(request.user)
    show_form_alert = len(pending_forms) > 0
    
    # Get form status for all team members
    form_status = submission.get_investigator_form_status()
    
    return render(request, 'submission/version_history.html', {
        'submission': submission,
        'histories': histories,
        'pending_forms': pending_forms,
        'show_form_alert': show_form_alert,
        'form_status': form_status,
        'can_submit': submission.can_user_submit(request.user)
    })

@login_required
def compare_version(request, submission_id, version):
    """Compare a version with its previous version."""
    submission = get_object_or_404(Submission, pk=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # Can't compare version 1 as it has no previous version
    if version <= 1:
        messages.error(request, "Version 1 cannot be compared as it has no previous version.")
        return redirect('submission:version_history', submission_id=submission_id)

    previous_version = version - 1
    comparison_data = []
    
    # Get all forms associated with this submission's study type
    forms = submission.study_type.forms.all()
    
    for form in forms:
        # Get entries for both versions
        entries_previous = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=previous_version
        ).select_related('form')
        
        entries_current = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version
        ).select_related('form')

        # Convert entries to dictionaries for easier comparison
        data_previous = {entry.field_name: entry.value for entry in entries_previous}
        data_current = {entry.field_name: entry.value for entry in entries_current}

        # Get field display names from form definition
        field_definitions = {
            field.name: field.displayed_name 
            for field in form.fields.all()
        }

        # Compare fields
        form_changes = []
        all_fields = sorted(set(data_previous.keys()) | set(data_current.keys()))
        
        for field in all_fields:
            displayed_name = field_definitions.get(field, field)
            value_previous = data_previous.get(field, 'Not provided')
            value_current = data_current.get(field, 'Not provided')

            # Handle JSON array values (e.g., checkbox selections)
            try:
                if isinstance(value_previous, str) and value_previous.startswith('['):
                    value_previous_display = ', '.join(json.loads(value_previous))
                else:
                    value_previous_display = value_previous
                    
                if isinstance(value_current, str) and value_current.startswith('['):
                    value_current_display = ', '.join(json.loads(value_current))
                else:
                    value_current_display = value_current
            except json.JSONDecodeError:
                value_previous_display = value_previous
                value_current_display = value_current

            # Only add to changes if values are different
            if value_previous != value_current:
                form_changes.append({
                    'field': displayed_name,
                    'previous_value': value_previous_display,
                    'current_value': value_current_display
                })

        # Only add form to comparison data if it has changes
        if form_changes:
            comparison_data.append({
                'form_name': form.name,
                'changes': form_changes
            })

    return render(request, 'submission/compare_versions.html', {
        'submission': submission,
        'version': version,
        'previous_version': previous_version,
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
            version = submission.version 
            print(f"Version is {version}")
            
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
        Q(khcc_number__icontains=term)
    ).distinct()[:10]

    results = []
    for submission in submissions:
        label = f"{submission.title}"
        if submission.khcc_number:
            label += f" (IRB: {submission.khcc_number})"
        results.append({
            'id': submission.temporary_id,
            'text': label
        })

    return JsonResponse({'results': results}, safe=False)




@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    versions = submission.version_histories.all()
    return render(request, 'submission/submission_detail.html', {
        'submission': submission,
        'versions': versions
    })

@login_required
def view_version(request, submission_id, version_number):
    """View a specific version of a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')

    # Check if version exists
    version_history = get_object_or_404(
        VersionHistory, 
        submission=submission, 
        version=version_number
    )

    # Get form data for this version
    form_data = {}
    for form in submission.study_type.forms.all():
        entries = FormDataEntry.objects.filter(
            submission=submission,
            form=form,
            version=version_number
        ).select_related('form')
        
        form_data[form.name] = {
            'form': form,
            'entries': {entry.field_name: entry.value for entry in entries}
        }

    # Get documents that existed at this version
    # You might need to adjust this depending on how you track document versions
    documents = submission.documents.filter(
        uploaded_at__lte=version_history.date
    )

    context = {
        'submission': submission,
        'version_number': version_number,
        'version_history': version_history,
        'form_data': form_data,
        'documents': documents,
        'is_current_version': version_number == submission.version,
    }
    
    return render(request, 'submission/view_version.html', context)


@login_required
def investigator_form(request, submission_id, form_id):
    """Handle investigator form submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    form = get_object_or_404(DynamicForm, pk=form_id)
    
    # Check if user is part of the research team
    if not (request.user == submission.primary_investigator or 
            submission.coinvestigators.filter(user=request.user).exists() or
            submission.research_assistants.filter(user=request.user).exists()):
        messages.error(request, "You are not authorized to submit this form.")
        return redirect('submission:dashboard')
    
    # Check if form should be filled by this user
    if not form.requested_per_investigator:
        messages.error(request, "This form is not required for individual submission.")
        return redirect('submission:dashboard')
    
    # Check if form is already submitted for this version
    existing_submission = InvestigatorFormSubmission.objects.filter(
        submission=submission,
        form=form,
        investigator=request.user,
        version=submission.version
    ).first()

    if existing_submission and not request.GET.get('view'):
        messages.info(request, "You have already submitted this form for the current version.")
        return redirect('submission:version_history', submission_id=submission.temporary_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit_form':
            form_class = generate_django_form(form)
            form_instance = form_class(request.POST)
            
            if form_instance.is_valid():
                try:
                    with transaction.atomic():
                        # Save form data
                        for field_name, value in form_instance.cleaned_data.items():
                            FormDataEntry.objects.create(
                                submission=submission,
                                form=form,
                                field_name=field_name,
                                value=value,
                                version=submission.version
                            )
                        
                        # Record form submission
                        InvestigatorFormSubmission.objects.create(
                            submission=submission,
                            form=form,
                            investigator=request.user,
                            version=submission.version
                        )

                        # Check if all forms are complete and update status if needed
                        if submission.are_all_investigator_forms_complete():
                            # Update submission status if it was pending documents
                            if submission.status == 'document_missing':
                                submission.status = 'submitted'
                                submission.save()
                                notify_form_completion(submission)
                                notify_osar_of_completion(submission)

                        messages.success(request, f"Form '{form.name}' submitted successfully.")
                        return redirect('submission:version_history', submission_id=submission.temporary_id)
                        
                except Exception as e:
                    logger.error(f"Error saving investigator form: {str(e)}")
                    messages.error(request, "An error occurred while saving your form.")
            else:
                messages.error(request, "Please correct the errors in the form.")
        
        elif action == 'back':
            return redirect('submission:version_history', submission_id=submission.temporary_id)
    else:
        # If viewing existing submission, populate with saved data
        if existing_submission:
            initial_data = {}
            saved_entries = FormDataEntry.objects.filter(
                submission=submission,
                form=form,
                version=submission.version
            )
            for entry in saved_entries:
                initial_data[entry.field_name] = entry.value
            form_class = generate_django_form(form)
            form_instance = form_class(initial=initial_data)
            form_instance.is_viewing = True  # Flag to make form read-only in template
        else:
            form_class = generate_django_form(form)
            form_instance = form_class()

    context = {
        'form': form_instance,
        'dynamic_form': form,
        'submission': submission,
        'is_viewing': request.GET.get('view') == 'true' or (existing_submission and not form.allow_updates),
        'existing_submission': existing_submission
    }
    
    return render(request, 'submission/investigator_form.html', context)

def notify_form_completion(submission):
    """Notify research team when all forms are complete."""
    system_user = get_system_user()
    
    # Get all team members
    recipients = []
    recipients.append(submission.primary_investigator)
    recipients.extend([ci.user for ci in submission.coinvestigators.all()])
    recipients.extend([ra.user for ra in submission.research_assistants.all()])
    
    # Create notification message
    message = Message.objects.create(
        sender=system_user,
        subject=f'All Required Forms Completed - {submission.title}',
        body=f"""
All required investigator forms have been completed for:

Submission ID: {submission.temporary_id}
Title: {submission.title}

The submission status has been updated to "Submitted" and is now under review.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    
    # Add recipients
    for recipient in recipients:
        message.recipients.add(recipient)


@login_required
def check_form_status(request, submission_id):
    """AJAX endpoint to check form completion status."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not submission.can_user_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    # Get pending forms for the current user
    pending_forms = submission.get_pending_investigator_forms(request.user)
    
    # Get overall form status
    form_status = submission.get_investigator_form_status()
    all_complete = submission.are_all_investigator_forms_complete()
    
    return JsonResponse({
        'pending_forms': [
            {'id': form.id, 'name': form.name} 
            for form in pending_forms
        ],
        'form_status': form_status,
        'all_complete': all_complete
    })

@login_required
def archive_submission(request, submission_id):
    """Archive a submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if request.method == 'POST':
        try:
            submission.is_archived = True
            submission.archived_at = timezone.now()
            submission.save(update_fields=['is_archived', 'archived_at'])
            messages.success(request, f'Submission "{submission.title}" has been archived.')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def unarchive_submission(request, submission_id):
    """Unarchive a submission."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if request.method == 'POST':
        try:
            submission.is_archived = False
            submission.archived_at = None
            submission.save(update_fields=['is_archived', 'archived_at'])
            messages.success(request, f'Submission "{submission.title}" has been unarchived.')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def archived_dashboard(request):
    """Display archived submissions dashboard."""
    submissions = Submission.objects.filter(
        is_archived=True
    ).select_related(
        'primary_investigator__userprofile'
    ).order_by('-date_created')

    return render(request, 'submission/archived_dashboard.html', {
        'submissions': submissions,
    })

@login_required
def view_submission(request, submission_id):
    """View submission details."""
    submission = get_object_or_404(Submission, temporary_id=submission_id)
    if not has_edit_permission(request.user, submission):
        messages.error(request, "You do not have permission to view this submission.")
        return redirect('submission:dashboard')
        
    context = {
        'submission': submission,
        'versions': submission.version_histories.all().order_by('-version'),
    }
    return render(request, 'submission/view_submission.html', context)


# Add to views.py

def handle_study_action_form(request, submission_id, form_name, action_type):
    """Generic handler for study action forms"""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not (request.user == submission.primary_investigator or 
            submission.coinvestigators.filter(user=request.user, can_submit=True).exists() or
            submission.research_assistants.filter(user=request.user, can_submit=True).exists()):
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('submission:version_history', submission_id=submission.temporary_id)
    
    # Get the dynamic form
    try:
        dynamic_form = DynamicForm.objects.get(name=form_name)
    except DynamicForm.DoesNotExist:
        messages.error(request, f"Required form '{form_name}' not found.")
        return redirect('submission:version_history', submission_id=submission.temporary_id)

    if request.method == 'POST':
        # Check for exit without save action first
        if request.POST.get('action') == 'exit_no_save':
            return redirect('submission:submission_actions', submission_id=submission.temporary_id)
            
        form_class = generate_django_form(dynamic_form)
        form = form_class(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create study action record
                    study_action = StudyAction.objects.create(
                        submission=submission,
                        action_type=action_type,
                        performed_by=request.user,
                        status='completed'
                    )
                    
                    # Save form data
                    for field_name, value in form.cleaned_data.items():
                        FormDataEntry.objects.create(
                            submission=submission,
                            form=dynamic_form,
                            field_name=field_name,
                            value=value,
                            version=submission.version
                        )
                    
                    # Handle specific actions
                    if action_type == 'withdrawal':
                        submission.status = 'withdrawn'
                        submission.is_locked = True
                        action_msg = "Study has been withdrawn"
                    elif action_type == 'closure':
                        submission.status = 'closed'
                        submission.is_locked = True
                        action_msg = "Study has been closed"
                    elif action_type == 'progress':
                        action_msg = "Progress report submitted"
                    elif action_type == 'amendment':
                        action_msg = "Amendment submitted"
                    
                    submission.save()
                    
                    # Send notifications
                    system_user = get_system_user()
                    
                    # Notify OSAR
                    osar_message = Message.objects.create(
                        sender=system_user,
                        subject=f"{action_type.title()} - {submission.title}",
                        body=f"""
A {action_type} has been submitted for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
PI: {submission.primary_investigator.get_full_name()}
Submitted by: {request.user.get_full_name()}

Please review the submitted {action_type} form.

Best regards,
AIDI System
                        """.strip(),
                        related_submission=submission
                    )
                    
                    # Add OSAR recipients
                    osar_users = User.objects.filter(groups__name='OSAR')
                    for user in osar_users:
                        osar_message.recipients.add(user)
                    
                    # Notify research team
                    team_message = Message.objects.create(
                        sender=system_user,
                        subject=f"{action_type.title()} - {submission.title}",
                        body=f"""
A {action_type} has been submitted for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Submitted by: {request.user.get_full_name()}

Status: {action_msg}

Best regards,
AIDI System
                        """.strip(),
                        related_submission=submission
                    )
                    
                    # Add research team recipients
                    team_message.recipients.add(submission.primary_investigator)
                    for coinv in submission.coinvestigators.all():
                        team_message.recipients.add(coinv.user)
                    for ra in submission.research_assistants.all():
                        team_message.recipients.add(ra.user)

                    messages.success(request, f"{action_msg} successfully.")
                    return redirect('submission:version_history', submission_id=submission.temporary_id)
                    
            except Exception as e:
                messages.error(request, f"Error processing {action_type}: {str(e)}")
                return redirect('submission:version_history', submission_id=submission.temporary_id)
    else:
        form_class = generate_django_form(dynamic_form)
        form = form_class()

    return render(request, 'submission/dynamic_actions.html', {
        'form': form,
        'submission': submission,
        'dynamic_form': dynamic_form,
    })

@login_required
def study_withdrawal(request, submission_id):
    return handle_study_action_form(request, submission_id, 'withdrawal', 'withdrawal')

@login_required
def progress_report(request, submission_id):
    return handle_study_action_form(request, submission_id, 'progress', 'progress')

@login_required
def study_amendment(request, submission_id):
    return handle_study_action_form(request, submission_id, 'amendment', 'amendment')

@login_required
def study_closure(request, submission_id):
    return handle_study_action_form(request, submission_id, 'closure', 'closure')


@login_required
def submission_actions(request, submission_id):
    """Display available actions for a submission."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check if user can submit
    can_submit = (
        request.user == submission.primary_investigator or
        submission.coinvestigators.filter(user=request.user, can_submit=True).exists() or
        submission.research_assistants.filter(user=request.user, can_submit=True).exists()
    )
    
    context = {
        'submission': submission,
        'can_submit': can_submit,
    }
    return render(request, 'submission/submission_actions.html', context)

@login_required
def download_action_pdf(request, submission_id, action_id):
    """Generate and download PDF for a specific study action."""
    try:
        submission = get_object_or_404(Submission, pk=submission_id)
        action = get_object_or_404(StudyAction, pk=action_id, submission=submission)
        
        # Use a fallback version if action.version is None
        version = action.version or submission.version
        
        # Generate PDF
        response = generate_submission_pdf(
            submission=submission,
            version=version,
            user=request.user,
            as_buffer=False,
            action_type=action.action_type,  # Pass action_type instead of action object
            action_date=action.date_created  # Pass action date if needed
        )
        
        if response is None:
            messages.error(request, "Error generating PDF. Please try again later.")
            logger.error(f"PDF generation failed for action {action_id}")
            return redirect('submission:version_history', submission_id=submission_id)
            
        # Modify the filename to include action type
        response['Content-Disposition'] = (
            f'attachment; filename="submission_{submission.temporary_id}_'
            f'{action.action_type}_{action.date_created.strftime("%Y%m%d")}.pdf"'
        )
            
        return response

    except Exception as e:
        logger.error(f"Error in download_action_pdf: {str(e)}")
        logger.error("Error details:", exc_info=True)
        messages.error(request, "An error occurred while generating the PDF.")
        return redirect('submission:version_history', submission_id=submission_id)
    

def notify_pending_forms(submission):
    """Notify team members of their pending forms."""
    system_user = get_system_user()
    required_forms = submission.get_required_investigator_forms()
    
    if not required_forms.exists():
        return
        
    # Get all team members who need to fill forms
    team_members = []
    team_members.extend([ci.user for ci in submission.coinvestigators.all()])
    team_members.extend([ra.user for ra in submission.research_assistants.all()])

    # For each team member, check their pending forms
    for member in team_members:
        pending_forms = []
        for form in required_forms:
            if not InvestigatorFormSubmission.objects.filter(
                submission=submission,
                form=form,
                investigator=member,
                version=submission.version
            ).exists():
                pending_forms.append(form.name)
        
        if pending_forms:
            # Create personalized notification for each member
            message = Message.objects.create(
                sender=system_user,
                subject=f'Required Forms for Submission - {submission.title}',
                body=f"""
Dear {member.get_full_name()},

You have pending forms to complete for:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Primary Investigator: {submission.primary_investigator.get_full_name()}

Required Forms:
{chr(10).join('- ' + form for form in pending_forms)}

Please log in to complete these forms at your earliest convenience. The submission cannot proceed until all required forms are completed.

Best regards,
AIDI System
                """.strip(),
                related_submission=submission
            )
            message.recipients.add(member)

    # Notify PI about pending forms
    pi_message = Message.objects.create(
        sender=system_user,
        subject=f'Submission Status - {submission.title}',
        body=f"""
Dear {submission.primary_investigator.get_full_name()},

Your submission (ID: {submission.temporary_id}) has been processed, but some team members need to complete required forms.

The submission will be marked as "Submitted" and sent for review once all forms are completed.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    pi_message.recipients.add(submission.primary_investigator)

def notify_osar_of_completion(submission):
    """Notify OSAR when all forms are complete and submission is ready for review."""
    system_user = get_system_user()
    osar_members = User.objects.filter(groups__name='OSAR')
    
    if not osar_members.exists():
        logger.warning("No OSAR members found for notification")
        return
        
    # Generate PDF of the submission
    try:
        buffer = generate_submission_pdf(
            submission=submission,
            version=submission.version,
            user=None,  # You can specify a user if required
            as_buffer=True
        )
        if not buffer:
            raise ValueError("Failed to generate PDF for submission")
    except Exception as e:
        logger.error(f"Failed to generate PDF for submission {submission.temporary_id}: {str(e)}")
        buffer = None
        
    # Create notification message
    message = Message.objects.create(
        sender=system_user,
        subject=f'Submission Ready for Review - {submission.title}',
        body=f"""
A submission has completed all required forms and is ready for review:

Submission ID: {submission.temporary_id}
Title: {submission.title}
Primary Investigator: {submission.primary_investigator.get_full_name()}
Study Type: {submission.study_type.name}
Date Submitted: {timezone.now().strftime('%Y-%m-%d %H:%M')}

The submission is now ready for your review.

Best regards,
AIDI System
        """.strip(),
        related_submission=submission
    )
    
    # Attach PDF if generated successfully
    if buffer:
        pdf_filename = f"submission_{submission.temporary_id}_v{submission.version}.pdf"
        message_attachment = MessageAttachment(message=message)
        message_attachment.file.save(pdf_filename, ContentFile(buffer.getvalue()))
    
    # Add OSAR members as recipients
    for member in osar_members:
        message.recipients.add(member)
