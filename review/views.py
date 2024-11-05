# review/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, F, Count, Case, When, Value, IntegerField
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db import transaction
from .models import ReviewRequest, Review, FormResponse, get_status_choices
from datetime import timedelta, datetime
from io import BytesIO
import json

from .models import ReviewRequest, Review, FormResponse
from .forms import ReviewRequestForm, ConflictOfInterestForm
from submission.models import Submission
from forms_builder.models import DynamicForm, StudyType
from .utils.pdf_generator import generate_review_dashboard_pdf
from messaging.models import Message
from users.utils import get_system_user  # Changed import to correct location

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


@login_required
def review_dashboard(request):
    """
    Display the review dashboard showing pending and completed reviews.
    Supports filtering, searching, and DataTables integration.
    """
    # Get filter parameters from request
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    study_type = request.GET.get('study_type', '')
    
    # Base queryset for pending reviews with all necessary related data
    pending_reviews = ReviewRequest.objects.filter(
        requested_to=request.user
    ).select_related(
        'submission__study_type',
        'requested_by__userprofile',
        'submission__primary_investigator__userprofile'
    ).annotate(
        days_until_deadline=Case(
            When(
                deadline__gt=timezone.now().date(),
                then=F('deadline') - timezone.now().date()
            ),
            default=Value(0),
            output_field=IntegerField(),
        )
    )

    # Apply filters if provided
    if status:
        pending_reviews = pending_reviews.filter(status=status)
    if date_from:
        pending_reviews = pending_reviews.filter(deadline__gte=date_from)
    if date_to:
        pending_reviews = pending_reviews.filter(deadline__lte=date_to)
    if study_type:
        pending_reviews = pending_reviews.filter(submission__study_type=study_type)

    # Get completed reviews
    completed_reviews = Review.objects.filter(
        reviewer=request.user
    ).select_related(
        'submission__study_type',
        'submission__primary_investigator__userprofile',
        'review_request'
    ).order_by('-date_submitted')

    # Handle DataTables AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Handle search
        if search_value:
            pending_reviews = pending_reviews.filter(
                Q(submission__title__icontains=search_value) |
                Q(submission__primary_investigator__userprofile__full_name__icontains=search_value) |
                Q(submission__study_type__name__icontains=search_value)
            )
        
        # Total records before filtering
        total_records = pending_reviews.count()
        
        # Handle ordering
        order_column = request.GET.get('order[0][column]', '0')
        order_dir = request.GET.get('order[0][dir]', 'asc')
        
        # Define orderable columns
        order_columns = {
            '0': 'submission__title',
            '1': 'submission__primary_investigator__userprofile__full_name',
            '2': 'submission__study_type__name',
            '3': 'deadline',
            '4': 'status',
            '5': 'days_until_deadline'
        }
        
        if order_dir == 'desc':
            order_by = f"-{order_columns[order_column]}"
        else:
            order_by = order_columns[order_column]
        
        pending_reviews = pending_reviews.order_by(order_by)
        
        # Pagination
        pending_reviews = pending_reviews[start:start + length]
        
        # Prepare data for response
        data = []
        for review in pending_reviews:
            data.append({
                'title': review.submission.title,
                'investigator': review.submission.primary_investigator.userprofile.full_name,
                'study_type': review.submission.study_type.name,
                'deadline': review.deadline.strftime('%Y-%m-%d'),
                'status': review.get_status_display(),
                'days_remaining': review.days_until_deadline,
                'actions': render_to_string('review/includes/review_actions.html', {
                    'review': review,
                    'user': request.user
                })
            })
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })

    # Prepare context for template rendering
    context = {
        'pending_reviews': pending_reviews[:10],  # Initial load limited to 10
        'completed_reviews': completed_reviews,
        'study_types': StudyType.objects.all(),
        'status_choices': [
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('completed', 'Completed'),
            ('declined', 'Declined'),
            ('overdue', 'Overdue')
        ]
    }
    
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

@login_required
def submit_review(request, review_request_id):
    review_request = get_object_or_404(ReviewRequest, pk=review_request_id)

      # Check if user can access this submission
    if not request.user.has_perm('submission.can_view_submission', review_request.submission):
        raise PermissionDenied
    
    if request.user != review_request.requested_to:
        return HttpResponseForbidden()
        
    if review_request.conflict_of_interest_declared is None:
        if request.method == 'POST':
            form = ConflictOfInterestForm(request.POST)
            if form.is_valid():
                has_conflict = form.cleaned_data['conflict_of_interest'] == 'yes'
                review_request.conflict_of_interest_declared = has_conflict
                if has_conflict:
                    review_request.conflict_of_interest_details = form.cleaned_data['conflict_details']
                    review_request.status = 'declined'
                else:
                    review_request.status = 'accepted'
                review_request.save()
                return redirect('review:dashboard')
        else:
            form = ConflictOfInterestForm()
        return render(request, 'review/conflict_of_interest.html', {
            'form': form,
            'review_request': review_request
        })
    
    # Handle review submission
    if request.method == 'POST':
        forms_valid = True
        form_responses = []
        
        for dynamic_form in review_request.selected_forms.all():
            form = FormForForm(dynamic_form, request.POST, prefix=f'form_{dynamic_form.id}')
            if form.is_valid():
                form_responses.append((dynamic_form, form))
            else:
                forms_valid = False
                break
        
        if forms_valid:
            review = Review.objects.create(
                review_request=review_request,
                reviewer=request.user,
                submission=review_request.submission,
                submission_version=review_request.submission_version,
                comments=request.POST.get('comments', '')
            )
            
            for dynamic_form, form in form_responses:
                FormResponse.objects.create(
                    review=review,
                    form=dynamic_form,
                    response_data=form.cleaned_data
                )
            
            review_request.status = 'completed'
            review_request.save()
            messages.success(request, 'Review submitted successfully.')
            return redirect('review:dashboard')
    
    return render(request, 'review/submit_review.html', {
        'review_request': review_request,
        'forms': [FormForForm(form, prefix=f'form_{form.id}') 
                 for form in review_request.selected_forms.all()]
    })


