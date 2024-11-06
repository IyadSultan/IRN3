# review/views.py
from datetime import timedelta, datetime
from io import BytesIO
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F, Count, Case, When, Value, IntegerField
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .forms import ReviewRequestForm, ConflictOfInterestForm
from .models import ReviewRequest, Review, FormResponse, get_status_choices
from .utils.pdf_generator import generate_review_dashboard_pdf
from forms_builder.models import DynamicForm, StudyType
from messaging.models import Message
from submission.models import Submission
from users.utils import get_system_user

# Rest of your view functions...

@login_required
def decline_review(request, review_id):
    """Handle declining a review request."""
    review_request = get_object_or_404(ReviewRequest, pk=review_id)
    
    # Verify permissions
    if request.user != review_request.requested_to:
        messages.error(request, "You don't have permission to decline this review.")
        return redirect('review:review_dashboard')

    # Check if review can be declined
    if review_request.status not in ['pending', 'accepted']:
        messages.error(request, "This review can no longer be declined.")
        return redirect('review:review_dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                reason = request.POST.get('reason')
                
                if not reason:
                    raise ValueError("Please provide a reason for declining the review.")

                # Update review request status
                review_request.status = 'declined'
                review_request.conflict_of_interest_declared = True
                review_request.conflict_of_interest_details = reason
                review_request.save()

                # Create notification message
                system_user = get_system_user()
                
                message = Message.objects.create(
                    sender=system_user,
                    subject=f'Review Request Declined - {review_request.submission.title}',
                    body=f"""
Dear {review_request.requested_by.userprofile.full_name},

The review request for "{review_request.submission.title}" has been declined by {request.user.userprofile.full_name}.

Reason provided:
{reason}

Please assign a different reviewer.

Best regards,
AIDI System
                    """.strip(),
                    study_name=review_request.submission.title,
                    related_submission=review_request.submission
                )
                
                # Add recipients
                message.recipients.add(review_request.requested_by)
                if review_request.submission.primary_investigator != review_request.requested_by:
                    message.cc.add(review_request.submission.primary_investigator)
                
                messages.success(request, "Review request declined successfully.")
                return redirect('review:review_dashboard')
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error declining review: {str(e)}")
    
    context = {
        'review_request': review_request,
    }
    return render(request, 'review/decline_review.html', context)


@login_required
def request_extension(request, review_id):
    """Handle review deadline extension requests."""
    review_request = get_object_or_404(ReviewRequest, pk=review_id)
    
    # Verify permissions
    if request.user != review_request.requested_to:
        messages.error(request, "You don't have permission to request an extension for this review.")
        return redirect('review:review_dashboard')

    # Check if review is still pending
    if review_request.status != 'pending':
        messages.error(request, "Can only request extensions for pending reviews.")
        return redirect('review:review_dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                new_deadline = request.POST.get('new_deadline')
                reason = request.POST.get('reason')
                
                if not new_deadline:
                    raise ValueError("New deadline is required")
                
                # Convert string to date
                new_deadline = timezone.datetime.strptime(new_deadline, '%Y-%m-%d').date()
                
                # Validate new deadline
                if new_deadline <= review_request.deadline:
                    raise ValueError("New deadline must be after current deadline")
                
                if new_deadline <= timezone.now().date():
                    raise ValueError("New deadline must be in the future")
                
                # Calculate extension days
                extension_days = (new_deadline - review_request.deadline).days
                
                # Create notification message
                message = Message.objects.create(
                    sender=request.user,
                    subject=f'Extension Request for Review #{review_id}',
                    body=f"""
Extension Request Details:
-------------------------
Review: {review_request.submission.title}
Current Deadline: {review_request.deadline}
Requested New Deadline: {new_deadline}
Extension Days: {extension_days} days
Reason: {reason}

Please review this request and respond accordingly.
                    """.strip(),
                    study_name=review_request.submission.title,
                    related_submission=review_request.submission
                )
                
                # Add recipients
                message.recipients.add(review_request.requested_by)
                
                # Update review request with pending extension
                review_request.extension_requested = True
                review_request.proposed_deadline = new_deadline
                review_request.extension_reason = reason
                review_request.save()
                
                messages.success(request, 
                    "Extension request submitted successfully. You will be notified once it's reviewed.")
                return redirect('review:review_dashboard')
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error submitting extension request: {str(e)}")
    
    context = {
        'review_request': review_request,
        'min_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'max_date': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
    }
    return render(request, 'review/request_extension.html', context)

@login_required
def view_review(request, review_id):
    """
    View a specific review and its form responses.
    """
    # Try to get the review first
    review = get_object_or_404(Review, pk=review_id)
    
    # Check permissions
    if not (request.user == review.reviewer or 
            request.user == review.review_request.requested_by or
            request.user == review.submission.primary_investigator):
        messages.error(request, "You don't have permission to view this review.")
        return redirect('review:review_dashboard')
    
    try:
        # Get all form responses for this review
        form_responses = FormResponse.objects.filter(
            review=review
        ).select_related(
            'form'  # Include the form information
        ).order_by(
            'form__order'  # Order by form order if specified
        )

        # Get the review request for context
        review_request = review.review_request

        # Get submission version at time of review
        submission = review.submission
        version_history = submission.version_histories.filter(
            version=review.submission_version
        ).first()

        context = {
            'review': review,
            'review_request': review_request,
            'form_responses': form_responses,
            'submission': submission,
            'version_history': version_history,
            'can_edit': request.user == review.reviewer and not review.is_completed,
            'is_pi': request.user == submission.primary_investigator,
            'is_requester': request.user == review_request.requested_by,
        }
        
        return render(request, 'review/view_review.html', context)

    except Exception as e:
        messages.error(request, f"Error retrieving review details: {str(e)}")
        return redirect('review:review_dashboard')


from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Case, When, Value, IntegerField
from django.urls import reverse
from django.utils import timezone

@login_required
def review_dashboard(request):
    """Enhanced dashboard showing role-specific views including OSAR coordinator's submissions."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Handle AJAX request for DataTables
        # Get filter parameters
        status = request.GET.get('status')
        study_type = request.GET.get('study_type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Base query for pending reviews
        pending_reviews = ReviewRequest.objects.filter(
            requested_to=request.user,
            status__in=['pending', 'accepted']
        ).select_related(
            'submission__study_type',
            'submission__primary_investigator__userprofile'
        ).annotate(
            days_remaining=Case(
                When(deadline__gt=timezone.now().date(),
                     then=F('deadline') - timezone.now().date()),
                default=Value(0),
                output_field=IntegerField(),
            )
        )

        # Apply filters
        if status:
            pending_reviews = pending_reviews.filter(status=status)
        if study_type:
            pending_reviews = pending_reviews.filter(submission__study_type_id=study_type)
        if date_from:
            pending_reviews = pending_reviews.filter(deadline__gte=date_from)
        if date_to:
            pending_reviews = pending_reviews.filter(deadline__lte=date_to)

        # Prepare data for DataTables
        data = []
        for review in pending_reviews:
            data.append({
                'title': review.submission.title,
                'investigator': review.submission.primary_investigator.userprofile.full_name,
                'study_type': review.submission.study_type.name,
                'deadline': review.deadline.strftime('%Y-%m-%d'),
                'status': review.get_status_display(),
                'days_remaining': review.days_remaining,
                'actions': f"""
                    <div class="btn-group">
                        <a href="{reverse('review:submit_review', args=[review.id])}" 
                           class="btn btn-sm btn-primary">
                            <i class="fas fa-edit"></i> Review
                        </a>
                        <button type="button" 
                                class="btn btn-sm btn-secondary dropdown-toggle"
                                data-bs-toggle="dropdown">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li>
                                <a class="dropdown-item" 
                                   href="{reverse('review:request_extension', args=[review.id])}">
                                    <i class="fas fa-clock"></i> Request Extension
                                </a>
                            </li>
                            <li>
                                <a class="dropdown-item" 
                                   href="{reverse('review:decline_review', args=[review.id])}">
                                    <i class="fas fa-times"></i> Decline Review
                                </a>
                            </li>
                        </ul>
                    </div>
                """
            })

        # Return JSON response
        return JsonResponse({
            'draw': int(request.GET.get('draw', 1)),
            'recordsTotal': pending_reviews.count(),
            'recordsFiltered': pending_reviews.count(),
            'data': data
        })

    # Handle regular GET request
    # Get completed reviews
    completed_reviews = Review.objects.filter(
        reviewer=request.user
    ).select_related(
        'submission__study_type',
        'submission__primary_investigator__userprofile'
    ).order_by('-date_submitted')

    # Get all study types for filter
    study_types = StudyType.objects.all()
    
    # Get status choices for filter
    status_choices = get_status_choices()

    context = {
        'completed_reviews': completed_reviews,
        'study_types': study_types,
        'status_choices': status_choices
    }
    # Fetch submissions needing review for OSAR coordinators
    
    if request.user.groups.filter(name='OSAR Coordinator').exists():
        submissions_needing_review = Submission.objects.filter(
            status='submitted'
                ).exclude(
                    review_requests__isnull=False
                ).select_related('primary_investigator__userprofile')

        context['submissions_needing_review'] = submissions_needing_review

    return render(request, 'review/dashboard.html', context)


    return render(request, 'review/dashboard.html', context)


@login_required
@permission_required('review.can_create_review_request', raise_exception=True)
def create_review_request(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if submission.status not in ['submitted', 'under_revision']:
        messages.error(request, 'This submission is not in a reviewable state.')
        return redirect('submission:detail', submission_id)
        
    if request.method == 'POST':
        form = ReviewRequestForm(request.POST)
        if form.is_valid():
            review_request = form.save(commit=False)
            review_request.submission = submission
            review_request.requested_by = request.user
            review_request.submission_version = submission.version
            review_request.save()
            form.save_m2m()
            
            messages.success(request, 'Review request created successfully.')
            return redirect('review:dashboard')
    else:
        form = ReviewRequestForm()
    
    return render(request, 'review/create_request.html', {
        'form': form,
        'submission': submission
    })

# review/views.py




@login_required
def submit_review(request, review_request_id):
    """Handle submission of a review."""
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

    # Check permissions
    if request.user != review_request.requested_to:
        return HttpResponseForbidden("You don't have permission to submit this review.")
    
    if review_request.status not in ['pending', 'accepted']:
        messages.error(request, "This review can no longer be submitted.")
        return redirect('review:review_dashboard')

    try:
        # Handle review submission
        if request.method == 'POST':
            with transaction.atomic():
                # Validate all forms
                forms_valid = True
                form_responses = []
                
                for dynamic_form in review_request.selected_forms.all():
                    form = FormForForm(
                        dynamic_form, 
                        request.POST, 
                        prefix=f'form_{dynamic_form.id}'
                    )
                    if form.is_valid():
                        form_responses.append((dynamic_form, form))
                    else:
                        forms_valid = False
                        break

                if not forms_valid:
                    raise ValueError("Please complete all required fields in the forms.")

                # Create review record
                review = Review.objects.create(
                    review_request=review_request,
                    reviewer=request.user,
                    submission=review_request.submission,
                    submission_version=review_request.submission_version,
                    comments=request.POST.get('comments', '')
                )

                # Save form responses
                for dynamic_form, form in form_responses:
                    FormResponse.objects.create(
                        review=review,
                        form=dynamic_form,
                        response_data=form.cleaned_data
                    )

                # Update review request status
                review_request.status = 'completed'
                review_request.save()

                # Send notification to requester and PI
                system_user = get_system_user()
                
                message = Message.objects.create(
                    sender=system_user,
                    subject=f'Review Completed - {review_request.submission.title}',
                    body=f"""
Dear {review_request.requested_by.userprofile.full_name},

The review for "{review_request.submission.title}" has been completed by {request.user.userprofile.full_name}.

You can view the review details here:
{request.build_absolute_uri(reverse('review:view_review', args=[review.id]))}

Best regards,
AIDI System
                    """.strip(),
                    study_name=review_request.submission.title,
                    related_submission=review_request.submission
                )

                # Add recipients
                message.recipients.add(review_request.requested_by)
                
                # CC the PI if different from requester
                if (review_request.submission.primary_investigator != 
                    review_request.requested_by):
                    message.cc.add(review_request.submission.primary_investigator)

                # Check if all required reviews are completed
                all_reviews_completed = check_all_reviews_completed(
                    review_request.submission
                )

                if all_reviews_completed:
                    # Update submission status
                    update_submission_after_reviews(
                        review_request.submission, 
                        request
                    )

                messages.success(request, "Review submitted successfully.")
                return redirect('review:review_dashboard')

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Error submitting review: {str(e)}")

    # Render form for GET or if there were errors
    context = {
        'review_request': review_request,
        'forms': [
            FormForForm(form, prefix=f'form_{form.id}')
            for form in review_request.selected_forms.all()
        ]
    }
    return render(request, 'review/submit_review.html', context)

def check_all_reviews_completed(submission):
    """Check if all required reviews for a submission are completed."""
    pending_reviews = ReviewRequest.objects.filter(
        submission=submission,
        status__in=['pending', 'accepted']
    ).exists()
    
    return not pending_reviews

def update_submission_after_reviews(submission, request):
    """Update submission status after all reviews are completed."""
    try:
        with transaction.atomic():
            # Get all completed reviews
            completed_reviews = Review.objects.filter(
                submission=submission,
                review_request__status='completed'
            ).select_related('reviewer', 'review_request')

            # Create notification about all reviews being completed
            system_user = get_system_user()
            
            message = Message.objects.create(
                sender=system_user,
                subject=f'All Reviews Completed - {submission.title}',
                body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

All requested reviews for your submission "{submission.title}" have been completed.

Reviews Summary:
{get_reviews_summary(completed_reviews)}

Next Steps:
1. The IRB coordinator will review all feedback
2. You will receive further instructions based on the review outcomes

Best regards,
AIDI System
                """.strip(),
                study_name=submission.title,
                related_submission=submission
            )

            # Add recipients
            message.recipients.add(submission.primary_investigator)
            
            # Update submission status
            submission.status = 'reviews_completed'
            submission.save()

    except Exception as e:
        messages.error(
            request, 
            f"Error updating submission after reviews: {str(e)}"
        )

def get_reviews_summary(completed_reviews):
    """Generate a summary of completed reviews."""
    summary = []
    for review in completed_reviews:
        summary.append(f"""
Reviewer: {review.reviewer.userprofile.full_name}
Completed: {review.date_submitted.strftime('%Y-%m-%d %H:%M')}
""".strip())
    
    return "\n\n".join(summary)

# review/views.py

@login_required
def review_summary(request, submission_id):
    """
    Display a summary of all reviews for a submission.
    Only accessible to PI, requester, and IRB coordinators.
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not (request.user == submission.primary_investigator or
            request.user.groups.filter(name='IRB Coordinator').exists() or
            submission.review_requests.filter(requested_by=request.user).exists()):
        messages.error(request, "You don't have permission to view this review summary.")
        return redirect('submission:dashboard')

    reviews = Review.objects.filter(
        submission=submission
    ).select_related(
        'reviewer__userprofile',
        'review_request'
    ).prefetch_related(
        'formresponse_set__form'
    ).order_by('date_submitted')

    context = {
        'submission': submission,
        'reviews': reviews,
        'can_make_decision': request.user.groups.filter(name='IRB Coordinator').exists()
    }
    return render(request, 'review/review_summary.html', context)

@login_required
def process_irb_decision(request, submission_id):
    """
    Process IRB coordinator's decision after reviewing all reviews.
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Check permissions
    if not request.user.groups.filter(name='IRB Coordinator').exists():
        messages.error(request, "You don't have permission to make IRB decisions.")
        return redirect('submission:dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                decision = request.POST.get('decision')
                comments = request.POST.get('comments')
                
                if not decision:
                    raise ValueError("Please select a decision")
                
                if decision not in ['approved', 'revision_required', 'rejected']:
                    raise ValueError("Invalid decision")

                # Update submission status
                submission.status = decision
                submission.save()
                
                # Create version history entry
                VersionHistory.objects.create(
                    submission=submission,
                    version=submission.version,
                    status=decision,
                    date=timezone.now()
                )

                # Send notification to PI
                system_user = get_system_user()
                
                message = Message.objects.create(
                    sender=system_user,
                    subject=f'IRB Decision - {submission.title}',
                    body=f"""
Dear {submission.primary_investigator.userprofile.full_name},

The IRB has made a decision regarding your submission "{submission.title}".

Decision: {decision.replace('_', ' ').title()}

{comments if comments else ''}

{'Please review the comments and submit a revised version.' if decision == 'revision_required' else ''}

Best regards,
AIDI System
                    """.strip(),
                    study_name=submission.title,
                    related_submission=submission
                )
                
                message.recipients.add(submission.primary_investigator)
                
                # Handle each decision type
                if decision == 'revision_required':
                    submission.version += 1
                    submission.save()
                    messages.success(request, 
                        "Decision recorded. PI has been notified to submit revisions.")
                
                elif decision == 'approved':
                    # Generate IRB approval number if not exists
                    if not submission.irb_number:
                        submission.irb_number = generate_irb_number(submission)
                        submission.save()
                    messages.success(request, 
                        "Submission approved. PI has been notified.")
                
                else:  # rejected
                    messages.success(request, 
                        "Submission rejected. PI has been notified.")

                return redirect('review:review_summary', submission_id=submission.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error processing decision: {str(e)}")
    
    context = {
        'submission': submission,
    }
    return render(request, 'review/process_decision.html', context)

def generate_irb_number(submission):
    """Generate a unique IRB number for approved submissions."""
    year = timezone.now().year
    # Get count of approved submissions this year
    count = Submission.objects.filter(
        status='approved',
        irb_number__startswith=f'IRB-{year}'
    ).count()
    
    # Format: IRB-YYYY-XXXX where XXXX is zero-padded sequential number
    return f'IRB-{year}-{(count + 1):04d}'



# submission/views.py






# review/views.py

@login_required
def forward_review(request, review_request_id):
    """Forward a review request to additional reviewers."""
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
    
    # Check permissions
    if not (request.user.groups.filter(name__in=[
        'OSAR Coordinator', 'IRB Head', 'Research Council Head', 'AHARPP Head'
    ]).exists() or review_request.can_forward):
        messages.error(request, "You don't have permission to forward review requests.")
        return redirect('review:review_dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                reviewer_ids = request.POST.getlist('reviewers')
                message = request.POST.get('message')
                deadline = request.POST.get('deadline')
                allow_forwarding = request.POST.get('allow_forwarding') == 'true'

                if not reviewer_ids:
                    raise ValueError("Please select at least one reviewer.")
                if not deadline:
                    raise ValueError("Please specify a deadline.")

                deadline_date = timezone.datetime.strptime(deadline, '%Y-%m-%d').date()
                if deadline_date <= timezone.now().date():
                    raise ValueError("Deadline must be in the future.")

                # Create new review requests
                for reviewer_id in reviewer_ids:
                    reviewer = User.objects.get(id=reviewer_id)
                    
                    # Create forwarded review request
                    new_request = ReviewRequest.objects.create(
                        submission=review_request.submission,
                        submission_version=review_request.submission_version,
                        requested_by=request.user,
                        requested_to=reviewer,
                        deadline=deadline_date,
                        message=message,
                        status='pending',
                        parent_request=review_request,
                        can_forward=allow_forwarding,
                        forwarding_chain=review_request.forwarding_chain + [request.user.id]
                    )

                    # Copy selected forms
                    new_request.selected_forms.set(review_request.selected_forms.all())

                    # Send notification
                    Message.objects.create(
                        sender=request.user,
                        subject=f'Forwarded Review Request - {review_request.submission.title}',
                        body=f"""
Dear {reviewer.userprofile.full_name},

A review request has been forwarded to you by {request.user.userprofile.full_name}.

Submission Details:
Title: {review_request.submission.title}
PI: {review_request.submission.primary_investigator.userprofile.full_name}
Deadline: {deadline_date.strftime('%Y-%m-%d')}

Message:
{message}

{'You are authorized to forward this review request to others.' if allow_forwarding else ''}

Please log in to the system to begin your review.

Best regards,
{request.user.userprofile.full_name}
                        """.strip(),
                        study_name=review_request.submission.title,
                        related_submission=review_request.submission
                    ).recipients.add(reviewer)

                messages.success(request, f"Review request forwarded to {len(reviewer_ids)} reviewer(s).")
                return redirect('review:review_dashboard')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error forwarding review request: {str(e)}")

    # Get available reviewers based on the user's role
    available_reviewers = get_available_reviewers(request.user, review_request.submission)

    context = {
        'review_request': review_request,
        'available_reviewers': available_reviewers,
        'min_date': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
        'suggested_date': (timezone.now() + timezone.timedelta(days=14)).strftime('%Y-%m-%d'),
        'user_role': get_user_primary_role(request.user)
    }
    return render(request, 'review/forward_review.html', context)

def get_available_reviewers(user, submission):
    """Get available reviewers based on user's role."""
    if user.groups.filter(name='OSAR Coordinator').exists():
        # OSAR can forward to heads of different committees
        return User.objects.filter(
            groups__name__in=['IRB Head', 'Research Council Head', 'AHARPP Head']
        ).exclude(
            review_requests__submission=submission
        ).select_related('userprofile')
    
    elif user.groups.filter(name='IRB Head').exists():
        # IRB Head can forward to IRB members
        return User.objects.filter(
            groups__name='IRB Member'
        ).exclude(
            review_requests__submission=submission
        ).select_related('userprofile')
    
    elif user.groups.filter(name='Research Council Head').exists():
        # RC Head can forward to RC members
        return User.objects.filter(
            groups__name='Research Council Member'
        ).exclude(
            review_requests__submission=submission
        ).select_related('userprofile')
    
    elif user.groups.filter(name='AHARPP Head').exists():
        # AHARPP Head can forward to AHARPP reviewers
        return User.objects.filter(
            groups__name='AHARPP Reviewer'
        ).exclude(
            review_requests__submission=submission
        ).select_related('userprofile')
    
    return User.objects.none()
