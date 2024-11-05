# review/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import ReviewRequest, Review, FormResponse
from .forms import ReviewRequestForm, ConflictOfInterestForm
from submission.models import Submission
from forms_builder.models import DynamicForm
from forms_builder.forms import FormForForm

@login_required
def review_dashboard(request):
    pending_reviews = ReviewRequest.objects.filter(
        requested_to=request.user,
        status__in=['pending', 'accepted']
    ).select_related('submission')
    
    completed_reviews = Review.objects.filter(
        reviewer=request.user
    ).select_related('submission')
    
    context = {
        'pending_reviews': pending_reviews,
        'completed_reviews': completed_reviews
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


