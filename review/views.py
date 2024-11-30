######################
# Imports
######################
from datetime import datetime, timedelta
import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView
from django import forms

from forms_builder.models import DynamicForm
from messaging.models import Message, MessageAttachment
from submission.models import Submission
from submission.utils.pdf_generator import PDFGenerator, generate_submission_pdf
from users.utils import get_system_user

from .forms import ReviewRequestForm
from .models import ReviewRequest, Review, FormResponse, NotepadEntry
from .utils.notifications import (
    send_review_request_notification,
    send_review_decline_notification,
    send_extension_request_notification,
    send_review_completion_notification,
    send_irb_decision_notification
)
from .utils.pdf_generator import generate_review_pdf
from iRN.constants import SUBMISSION_STATUS_CHOICES



######################
# Review Dashboard
# URL: path('', ReviewDashboardView.as_view(), name='review_dashboard'),
######################

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import ReviewRequest, Review
from submission.models import Submission

class ReviewDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'review/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        visible_submissions = Submission.get_visible_submissions_for_user(user)

        # Add group membership checks to context
        context.update({
            'is_osar_member': user.groups.filter(name='OSAR').exists(),
            'is_irb_member': user.groups.filter(name='IRB').exists(),
            'is_rc_member': user.groups.filter(name='RC').exists(),
            'is_aahrpp_member': user.groups.filter(name='AAHRPP').exists(),
            'submissions': visible_submissions,
        })

        # Get submissions needing review (for OSAR members)
        if context['is_osar_member']:
            submissions_needing_review = Submission.objects.filter(
                status='submitted'
            ).select_related(
                'primary_investigator__userprofile'
            )
            context['submissions_needing_review'] = submissions_needing_review

        # Get reviews that can be forwarded
        forwarded_reviews = ReviewRequest.objects.filter(
            Q(requested_to=user) | Q(requested_by=user),
            can_forward=True,
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        )
        context['forwarded_reviews'] = forwarded_reviews

        # Get pending reviews where user is the reviewer
        pending_reviews = ReviewRequest.objects.select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        ).filter(
            Q(requested_to=user) | Q(requested_by=user),
            status__in=['pending', 'overdue', 'extended']
        ).order_by('-created_at')
        context['pending_reviews'] = pending_reviews

        return context

class IRBDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'review/irb_dashboard.html'

    def test_func(self):
        return self.request.user.groups.filter(name='IRB').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get submissions marked for IRB review
        irb_submissions = Submission.objects.filter(
            show_in_irb=True
        ).select_related(
            'primary_investigator__userprofile',
            'study_type'
        )
        context['irb_submissions'] = irb_submissions

        # Get IRB-related review requests
        irb_reviews = ReviewRequest.objects.filter(
            Q(requested_to__groups__name='IRB') | Q(requested_by__groups__name='IRB'),
            Q(requested_to=user) | Q(requested_by=user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'submission__study_type',
            'requested_by',
            'requested_to'
        ).distinct()
        context['irb_reviews'] = irb_reviews

        return context

class RCDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'review/rc_dashboard.html'

    def test_func(self):
        return self.request.user.groups.filter(name='RC').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get submissions marked for RC review
        rc_submissions = Submission.objects.filter(
            show_in_rc=True
        ).select_related(
            'primary_investigator__userprofile',
            'study_type'
        )
        context['rc_submissions'] = rc_submissions

        # Get RC-related review requests
        rc_reviews = ReviewRequest.objects.filter(
            Q(requested_to__groups__name='RC') | Q(requested_by__groups__name='RC'),
            Q(requested_to=user) | Q(requested_by=user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'submission__study_type',
            'requested_by',
            'requested_to'
        ).distinct()
        context['rc_reviews'] = rc_reviews

        return context

######################
# Create Review Request
# URL: path('create/<int:submission_id>/', CreateReviewRequestView.as_view(), name='create_review_request'),
######################

from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import transaction
from messaging.models import Message

class CreateReviewRequestView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ReviewRequest
    form_class = ReviewRequestForm
    template_name = 'review/create_review_request.html'
    permission_required = 'review.can_create_review_request'

    def get_initial(self):
        initial = super().get_initial()
        initial['deadline'] = timezone.now().date() + timezone.timedelta(days=14)
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.submission = get_object_or_404(Submission, pk=self.kwargs['submission_id'])
        kwargs['study_type'] = self.submission.study_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.submission
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Set review request fields
                self.object = form.save(commit=False)
                self.object.submission = self.submission
                self.object.requested_by = self.request.user
                self.object.submission_version = self.submission.version
                self.object.save()
                form.save_m2m()

                # Update submission status to 'under_review'
                if self.submission.status == 'submitted':
                    self.submission.status = 'under_review'
                    self.submission.save(update_fields=['status'])

                # Generate the absolute URL for the review
                review_url = self.request.build_absolute_uri(
                    reverse('review:submit_review', args=[self.object.id])
                )

                # Create notification message for the reviewer
                message = Message.objects.create(
                    sender=self.request.user,
                    subject=f'Review Request: {self.submission.title}',
                    body=f"""Dear {self.object.requested_to.userprofile.full_name},

You have been requested to review the submission "{self.submission.title}" (Version {self.submission.version}).

Review Details:
- Deadline: {self.object.deadline.strftime('%B %d, %Y')}
- Forms to Complete: {', '.join(form.name for form in self.object.selected_forms.all())}

Message from requester:
{self.object.message if self.object.message else 'No additional message provided.'}

You can access the review directly by clicking the following link:
{review_url}

Alternatively, you can find this review in the "Reviews" section of your dashboard.

Important Deadlines:
- Review Due Date: {self.object.deadline.strftime('%B %d, %Y')}
- Days Remaining: {(self.object.deadline - timezone.now().date()).days} days

Best regards,
{self.request.user.userprofile.full_name}""",
                    related_submission=self.submission,
                )
                
                # Add the reviewer as recipient
                message.recipients.add(self.object.requested_to)
                
                messages.success(self.request, 'Review request created and notification sent successfully.')
                return redirect('review:review_dashboard')

        except Exception as e:
            messages.error(self.request, f'Error creating review request: {str(e)}')
            return super().form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
######################
# Decline Review
# URL: path('review/<int:review_request_id>/decline/', DeclineReviewView.as_view(), name='decline_review'),
######################

class DeclineReviewView(LoginRequiredMixin, View):
    template_name = 'review/decline_review.html'

    def dispatch(self, request, *args, **kwargs):
        self.review_request = self.get_review_request(kwargs['review_request_id'], request.user)
        if not self.review_request:
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'review_request': self.review_request})

    def post(self, request, *args, **kwargs):
        reason = request.POST.get('reason')
        if not reason:
            messages.error(request, "Please provide a reason for declining the review.")
            return redirect('review:decline_review', review_request_id=self.review_request.id)

        try:
            with transaction.atomic():
                self.review_request.status = 'declined'
                self.review_request.conflict_of_interest_declared = True
                self.review_request.conflict_of_interest_details = reason
                self.review_request.save()

                send_review_decline_notification(self.review_request, request.user, reason)
                messages.success(request, "Review request declined successfully.")
                return redirect('review:review_dashboard')
        except Exception as e:
            messages.error(request, f"Error declining review: {str(e)}")
            return redirect('review:decline_review', review_request_id=self.review_request.id)

    def get_review_request(self, review_request_id, user):
        review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
        if user != review_request.requested_to or review_request.status in ['completed', 'declined']:
            messages.error(self.request, "You don't have permission to decline this review.")
            return None
        return review_request


######################
# Request Extension
# URL: path('review/<int:review_id>/extension/', RequestExtensionView.as_view(), name='request_extension'),
######################

class RequestExtensionView(LoginRequiredMixin, FormView):
    template_name = 'review/request_extension.html'

    def get_review_request(self, review_request_id, user):
        review_request = get_object_or_404(ReviewRequest, pk=review_request_id)
        if user != review_request.requested_to or review_request.status not in ['pending', 'overdue', 'extended']:
            messages.error(self.request, "You don't have permission to request an extension for this review.")
            return None
        return review_request

    def dispatch(self, request, *args, **kwargs):
        self.review_request = self.get_review_request(kwargs['review_request_id'], request.user)
        if not self.review_request:
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'review_request': self.review_request})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_request'] = self.review_request
        context['min_date'] = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        context['max_date'] = (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        return context

    def post(self, request, *args, **kwargs):
        new_deadline = request.POST.get('new_deadline')
        reason = request.POST.get('reason')
        if not new_deadline or not reason:
            messages.error(request, "Please provide all required fields.")
            return self.form_invalid(None)

        try:
            new_deadline_date = timezone.datetime.strptime(new_deadline, '%Y-%m-%d').date()
            if new_deadline_date <= self.review_request.deadline or new_deadline_date <= timezone.now().date():
                raise ValueError("Invalid new deadline.")

            with transaction.atomic():
                send_extension_request_notification(
                    self.review_request,
                    new_deadline_date,
                    reason,
                    request.user
                )

                self.review_request.extension_requested = True
                self.review_request.proposed_deadline = new_deadline_date
                self.review_request.extension_reason = reason
                self.review_request.save()

                messages.success(request, "Extension request submitted successfully.")
                return redirect('review:review_dashboard')
        except ValueError as e:
            messages.error(request, str(e))
            return self.form_invalid(None)


######################
# Submit Review
# URL: path('submit/<int:review_request_id>/', SubmitReviewView.as_view(), name='submit_review'),
######################

class SubmitReviewView(LoginRequiredMixin, View):
    template_name = 'review/submit_review.html'

    def dispatch(self, request, *args, **kwargs):
        self.review_request = get_object_or_404(
            ReviewRequest.objects.select_related(
                'submission',
                'requested_by__userprofile',
                'submission__primary_investigator'
            ),
            pk=kwargs['review_request_id']
        )
        if not self.can_submit_review(request.user, self.review_request):
            raise PermissionDenied("You don't have permission to submit this review.")
        return super().dispatch(request, *args, **kwargs)

    def can_submit_review(self, user, review_request):
        return user == review_request.requested_to and review_request.status in ['pending', 'overdue', 'extended']

    def get(self, request, *args, **kwargs):
        forms_data = self.get_forms_data()
        context = {
            'review_request': self.review_request,
            'forms_data': forms_data,
            'submission': self.review_request.submission,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', '')
        forms_data = self.get_forms_data(request.POST)
        is_valid = all(form_data['form'].is_valid() for form_data in forms_data)

        if not is_valid:
            messages.error(request, "Please correct the errors in the form.")
            context = {
                'review_request': self.review_request,
                'forms_data': forms_data,
                'submission': self.review_request.submission,
            }
            return render(request, self.template_name, context)

        try:
            with transaction.atomic():
                review, _ = Review.objects.get_or_create(
                    review_request=self.review_request,
                    defaults={
                        'reviewer': request.user,
                        'submission': self.review_request.submission,
                        'submission_version': self.review_request.submission_version
                    }
                )

                for form_data in forms_data:
                    form_template = form_data['template']
                    form_instance = form_data['form']
                    response_data = form_instance.cleaned_data

                    FormResponse.objects.update_or_create(
                        review=review,
                        form=form_template,
                        defaults={'response_data': response_data}
                    )

                comments = request.POST.get('comments', '').strip()
                if comments:
                    review.comments = comments

                if action == 'submit':
                    review.is_completed = True
                    review.completed_at = timezone.now()
                    self.review_request.status = 'completed'
                    self.review_request.save()

                    # Generate PDF and send notification
                    pdf_buffer = generate_review_pdf(review, self.review_request.submission, review.formresponse_set.all())
                    if pdf_buffer:
                        send_review_completion_notification(review, self.review_request, pdf_buffer)
                        pdf_buffer.close()

                    messages.success(request, "Review submitted successfully.")
                else:
                    messages.success(request, "Review saved as draft.")

                review.save()
                return redirect('review:review_dashboard')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            context = {
                'review_request': self.review_request,
                'forms_data': forms_data,
                'submission': self.review_request.submission,
            }
            return render(request, self.template_name, context)

    def get_forms_data(self, data=None):
        forms_data = []
        for form_template in self.review_request.selected_forms.all():
            DynamicFormClass = self.generate_django_form(form_template)
            form_instance = DynamicFormClass(
                data=data,
                prefix=f'form_{form_template.id}'
            )
            forms_data.append({
                'template': form_template,
                'form': form_instance
            })
        return forms_data

    def generate_django_form(self, form_template):
        form_fields = {}
        field_map = {
            'text': forms.CharField,
            'email': forms.EmailField,
            'tel': forms.CharField,
            'number': forms.IntegerField,
            'date': forms.DateField,
            'textarea': forms.CharField,
            'checkbox': forms.MultipleChoiceField,
            'radio': forms.ChoiceField,
            'select': forms.ChoiceField,
            'choice': forms.MultipleChoiceField,
            'table': forms.CharField,
        }
        for field in form_template.fields.all():
            field_class = field_map.get(field.field_type, forms.CharField)
            field_kwargs = {
                'label': field.displayed_name,
                'required': field.required,
                'help_text': field.help_text,
                'initial': field.default_value,
            }
            if field.field_type in ['checkbox', 'radio', 'select', 'choice']:
                choices = [(choice.strip(), choice.strip())
                           for choice in field.choices.split(',')
                           if choice.strip()] if field.choices else []
                field_kwargs['choices'] = choices
            if field.max_length:
                field_kwargs['max_length'] = field.max_length
            if field.field_type == 'textarea':
                field_kwargs['widget'] = forms.Textarea(attrs={'rows': field.rows})
            form_fields[field.name] = field_class(**field_kwargs)
        return type(f'DynamicForm_{form_template.id}', (forms.Form,), form_fields)


######################
# View Review
# URL: path('review/<int:review_request_id>/', ViewReviewView.as_view(), name='view_review'),
######################

class ViewReviewView(LoginRequiredMixin, TemplateView):
    template_name = 'review/view_review.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the review request using review_request_id from kwargs
        review_request = get_object_or_404(ReviewRequest, id=kwargs['review_request_id'])
        
        # Then get the associated review
        self.review = get_object_or_404(
            Review.objects.select_related(
                'review_request',
                'reviewer__userprofile',
                'submission',
                'submission__primary_investigator'
            ),
            review_request=review_request
        )
        
        if not self.has_permission(request.user, self.review):
            messages.error(request, "You don't have permission to view this review.")
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, user, review):
        return user in [
            review.reviewer,
            review.review_request.requested_by,
            review.submission.primary_investigator
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'review': self.review,
            'review_request': self.review.review_request,
            'submission': self.review.submission,
            'reviewer': self.review.reviewer,
            'form_responses': FormResponse.objects.filter(review=self.review)
        })
        return context


######################
# Review Summary
# URL: path('submission/<int:submission_id>/summary/', ReviewSummaryView.as_view(), name='review_summary'),
######################

class ReviewSummaryView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View for displaying a comprehensive summary of a submission's reviews.
    Handles permissions and provides detailed context for different user roles.
    """
    template_name = 'review/review_summary.html'

    def test_func(self):
        """
        Verify if the current user has permission to view this submission's details.
        Permissions are based on user roles and submission ownership.
        """
        submission_id = self.kwargs.get('submission_id')
        self.submission = get_object_or_404(Submission, pk=submission_id)
        user = self.request.user

        # OSAR members can view all submissions
        if user.groups.filter(name='OSAR').exists():
            return True

        # IRB members can view all submissions
        if user.groups.filter(name='IRB').exists():
            return True

        # RC members can view any submission in their department
        if user.groups.filter(name='RC').exists():
            return user.userprofile.department == self.submission.primary_investigator.userprofile.department

        # Check if user is directly involved with the submission
        return user in [
            self.submission.primary_investigator,
            *self.submission.coinvestigators.all(),
            *self.submission.research_assistants.all()
        ]

    def handle_no_permission(self):
        """
        Handle cases where permission is denied.
        Provides appropriate redirect based on user role.
        """
        messages.error(self.request, "You don't have permission to view this submission's details.")
        
        # Route to appropriate dashboard based on user role
        user = self.request.user
        if user.groups.filter(name='OSAR').exists():
            return redirect('review:osar_dashboard')
        elif user.groups.filter(name='RC').exists():
            return redirect('review:rc_dashboard')
        elif user.groups.filter(name='IRB').exists():
            return redirect('review:irb_dashboard')
        else:
            return redirect('submission:dashboard')

    def get_review_requests(self):
        """
        Get all review requests for the submission with related data.
        """
        return ReviewRequest.objects.filter(
            submission=self.submission
        ).select_related(
            'requested_to__userprofile',
            'requested_by__userprofile',
            'submission__primary_investigator__userprofile'
        ).prefetch_related(
            'review_set',
            'review_set__formresponse_set__form'
        ).order_by('-created_at')

    def get_version_histories(self):
        """
        Get submission version histories ordered by version.
        """
        return self.submission.version_histories.all().order_by('-version')

    def get_user_permissions(self, user):
        """
        Determine user-specific permissions for the view.
        """
        return {
            'can_make_decision': user.groups.filter(name='IRB Coordinator').exists(),
            'can_download_pdf': True,  # Can be modified based on specific requirements
            'can_assign_irb': (user.groups.filter(name='IRB').exists() and 
                             not self.submission.khcc_number),
            'is_osar': user.groups.filter(name='OSAR').exists(),
            'is_rc': user.groups.filter(name='RC').exists(),
            'is_irb': user.groups.filter(name='IRB').exists(),
            'can_create_review': any([
                user.groups.filter(name=role).exists() 
                for role in ['OSAR', 'IRB', 'RC']
            ])
        }

    def get_submission_stats(self, review_requests):
        """
        Calculate submission-related statistics.
        """
        return {
            'total_reviews': review_requests.count(),
            'completed_reviews': review_requests.filter(status='completed').count(),
            'pending_reviews': review_requests.filter(status='pending').count(),
            'days_since_submission': (timezone.now().date() - 
                                    self.submission.date_submitted.date()).days
        }

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the review summary view.
        Shows submission history even if no reviews exist yet.
        """
        if not self.test_func():
            return self.handle_no_permission()

        # Get submission history data
        version_histories = self.get_version_histories()
        user_permissions = self.get_user_permissions(request.user)
        
        # Get review data if any exists
        review_requests = self.get_review_requests()
        submission_stats = self.get_submission_stats(review_requests) if review_requests.exists() else {
            'total_reviews': 0,
            'completed_reviews': 0,
            'pending_reviews': 0,
            'days_since_submission': (timezone.now().date() - 
                                    self.submission.date_submitted.date()).days
        }

        # Check for active reviews
        has_active_reviews = review_requests.filter(
            status__in=['pending', 'in_progress']
        ).exists() if review_requests.exists() else False

        context = {
            'submission': self.submission,
            'review_requests': review_requests,
            'version_histories': version_histories,
            'stats': submission_stats,
            'has_active_reviews': has_active_reviews,
            'has_reviews': review_requests.exists(),
            **user_permissions
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests (if any specific actions are needed).
        Currently redirects to GET as this is primarily a view-only page.
        """
        return self.get(request, *args, **kwargs)
######################
# Process IRB Decision
# URL: path('submission/<int:submission_id>/decision/', ProcessIRBDecisionView.as_view(), name='process_decision'),
######################

class ProcessIRBDecisionView(LoginRequiredMixin, FormView):
    template_name = 'review/process_decision.html'

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        if not request.user.groups.filter(name='IRB Coordinator').exists():
            messages.error(request, "You don't have permission to make IRB decisions.")
            return redirect('submission:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        decision = request.POST.get('decision')
        comments = request.POST.get('comments')

        if decision not in ['approved', 'revision_required', 'rejected']:
            messages.error(request, "Invalid decision.")
            return self.form_invalid(None)

        try:
            with transaction.atomic():
                self.submission.status = decision
                self.submission.save()

                send_irb_decision_notification(self.submission, decision, comments)

                messages.success(request, "Decision recorded and PI has been notified.")
                return redirect('review:review_summary', submission_id=self.submission.id)
        except Exception as e:
            messages.error(request, f"Error processing decision: {str(e)}")
            return self.form_invalid(None)


######################
# Submission Versions
# URL: path('submission/<int:submission_id>/versions/', SubmissionVersionsView.as_view(), name='submission_versions'),
######################

class SubmissionVersionsView(LoginRequiredMixin, TemplateView):
    template_name = 'review/submission_versions.html'

    def get(self, request, *args, **kwargs):
        submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        histories = submission.version_histories.order_by('-version')
        return render(request, self.template_name, {
            'submission': submission,
            'histories': histories,
        })

def download_review_pdf(request, review_request_id):
    review_request = get_object_or_404(ReviewRequest, id=review_request_id)
    review = get_object_or_404(
        Review.objects.select_related(
            'review_request',
            'reviewer__userprofile',
            'submission',
            'submission__primary_investigator'
        ),
        review_request=review_request
    )
    
    submission = review.submission
    form_responses = review.formresponse_set.all()
    
    # Create snake_case filename
    submission_title = slugify(submission.title).replace('-', '_')
    reviewer_name = slugify(review.reviewer.get_full_name()).replace('-', '_')
    date_str = datetime.now().strftime('%Y_%m_%d')
    
    filename = f"{submission_title}_{reviewer_name}_{date_str}.pdf"
    
    buffer = generate_review_pdf(review, submission, form_responses)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(buffer.getvalue())
    buffer.close()
    
    return response

class UserAutocompleteView(View):
    def get(self, request):
        term = request.GET.get('term', '')
        user_type = request.GET.get('user_type', '')
        
        if len(term) < 2:
            return JsonResponse([], safe=False)
            
        User = get_user_model()
        users = User.objects.filter(
            Q(first_name__icontains=term) | 
            Q(last_name__icontains=term) |
            Q(email__icontains=term)
        )
        
        # Add any additional filtering for reviewers here
        if user_type == 'reviewer':
            users = users.filter(groups__name='Reviewers')
            
        results = [
            {
                'id': user.id,
                'label': f"{user.get_full_name()} ({user.email})"
            }
            for user in users[:10]  # Limit to 10 results
        ]
        
        return JsonResponse(results, safe=False)


######################
# Assign KHCC #
# URL: path('submission/<int:submission_id>/assign-irb/', AssignKHCCNumberView.as_view(), name='assign_irb'),
######################

class AssignKHCCNumberView(LoginRequiredMixin, View):
    template_name = 'review/assign_khcc_number.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='OSAR').exists():
            messages.error(request, "You don't have permission to assign KHCC #s.")
            return redirect('review:review_dashboard')
        
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        if self.submission.khcc_number:
            messages.warning(request, "This submission already has a KHCC #.")
            return redirect('review:review_summary', submission_id=self.submission.id)
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'submission': self.submission,
            'suggested_irb': self._generate_khcc_number()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        khcc_number = request.POST.get('khcc_number', '').strip()
        
        if not khcc_number:
            messages.error(request, "KHCC # is required.")
            return redirect('review:assign_irb', submission_id=self.submission.temporary_id)

        # Check uniqueness
        if Submission.objects.filter(khcc_number=khcc_number).exists():
            messages.error(request, "This KHCC # is already in use. Please try another.")
            return redirect('review:assign_irb', submission_id=self.submission.temporary_id)

        try:
            with transaction.atomic():
                self.submission.khcc_number = khcc_number
                self.submission.save()

                # Get all users who need to be notified
                users_to_notify = set([self.submission.primary_investigator])
                
                # Add research assistants with submit privilege
                users_to_notify.update(
                    self.submission.research_assistants.filter(
                        can_submit=True
                    ).values_list('user', flat=True)
                )
                
                # Add co-investigators with submit privilege
                users_to_notify.update(
                    self.submission.coinvestigators.filter(
                        can_submit=True
                    ).values_list('user', flat=True)
                )

                # Send notification to each user
                system_user = get_system_user()
                message_content = f"""
                An KHCC # has been assigned to the submission "{self.submission.title}".
                KHCC #: {khcc_number}
                """

                for user in users_to_notify:
                    print("Debug - System User:", system_user)
                    print("Debug - Users to notify:", users_to_notify)
                    print("Debug - Message fields available:", [field.name for field in Message._meta.get_fields()])
                    print("Debug - Message content:", message_content)
                    try:
                        print(f"Debug - Creating message for user: {user}")
                        message = Message.objects.create(
                            sender=system_user,
                            body=message_content,
                            subject=f"KHCC # Assigned - {self.submission.title}",
                            related_submission=self.submission
                        )
                        message.recipients.set([user])  # Use set() method for many-to-many relationship
                        print(f"Debug - Message created successfully: {message}")
                    except Exception as e:
                        print(f"Debug - Message creation error: {str(e)}")
                        print(f"Debug - Error type: {type(e)}")
                        raise  # Re-raise the exception to trigger the outer error handling

                messages.success(request, f"KHCC # {khcc_number} has been assigned successfully.")
                return redirect('review:review_summary', submission_id=self.submission.temporary_id)

        except Exception as e:
            messages.error(request, f"Error assigning KHCC #: {str(e)}")
            return redirect('review:assign_irb', submission_id=self.submission.temporary_id)

    def _generate_khcc_number(self):
        """Generate a suggested KHCC # format: YYYY-XXX"""
        year = timezone.now().year
        
        # Get the highest number for this year
        latest_irb = Submission.objects.filter(
            khcc_number__startswith=f"{year}-"
        ).order_by('-khcc_number').first()

        if latest_irb and latest_irb.khcc_number:
            try:
                number = int(latest_irb.khcc_number.split('-')[1]) + 1
            except (IndexError, ValueError):
                number = 1
        else:
            number = 1

        return f"{year}-{number:03d}"

class ToggleSubmissionVisibilityView(LoginRequiredMixin, View):
    def post(self, request, submission_id):
        try:
            submission = get_object_or_404(Submission, temporary_id=submission_id)
            toggle_type = request.POST.get('toggle_type')
            
            if not toggle_type in ['irb', 'rc']:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid toggle type'
                }, status=400)
            
            if toggle_type == 'irb':
                submission.show_in_irb = not getattr(submission, 'show_in_irb', False)
                visible = submission.show_in_irb
            else:  # toggle_type == 'rc'
                submission.show_in_rc = not getattr(submission, 'show_in_rc', False)
                visible = submission.show_in_rc
            
            submission.save(update_fields=[f'show_in_{toggle_type}'])
            
            return JsonResponse({
                'status': 'success',
                'visible': visible,
                'message': f'Successfully toggled {toggle_type.upper()} visibility'
            })
            
        except Submission.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Submission not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class UpdateSubmissionStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['IRB', 'RC', 'OSAR']).exists()

    def post(self, request, submission_id):
        try:
            submission = get_object_or_404(Submission, temporary_id=submission_id)
            new_status = request.POST.get('status')
            
            if not new_status:
                return JsonResponse({
                    'status': 'error',
                    'message': 'New status not provided'
                }, status=400)
            
            # Get available status choices
            valid_statuses = [choice[0] for choice in submission.get_status_choices()]
            
            if new_status not in valid_statuses:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid status'
                }, status=400)
            
            # Update the status
            submission.status = new_status
            submission.save(update_fields=['status'])
            
            return JsonResponse({
                'status': 'success',
                'message': 'Status updated successfully',
                'new_status': new_status
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

  


@login_required
def irb_dashboard(request):
    if not request.user.groups.filter(name='IRB').exists():
        return redirect('review:review_dashboard')
    
    context = {
        'irb_submissions': Submission.objects.filter(
            status='submitted'
        ).select_related(
            'primary_investigator__userprofile'
        ),
        'pending_irb_decisions': Submission.objects.filter(
            status='pending_irb_decision'
        ).select_related(
            'primary_investigator__userprofile'
        ),
        'irb_reviews': ReviewRequest.objects.filter(
            Q(requested_to__groups__name='IRB') | Q(requested_by__groups__name='IRB'),
            Q(requested_to=request.user) | Q(requested_by=request.user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        ).distinct(),
    }
    return render(request, 'review/irb_dashboard.html', context)

@login_required
def rc_dashboard(request):
    if not request.user.groups.filter(name='RC').exists():
        return redirect('review:review_dashboard')
    
    context = {
        'rc_submissions': Submission.objects.filter(
            status='submitted'
        ).select_related(
            'primary_investigator__userprofile'
        ),
        'department_submissions': Submission.objects.filter(
            primary_investigator__userprofile__department=request.user.userprofile.department
        ).select_related(
            'primary_investigator__userprofile'
        ),
        'rc_reviews': ReviewRequest.objects.filter(
            Q(requested_to__groups__name='RC') | Q(requested_by__groups__name='RC'),
            Q(requested_to=request.user) | Q(requested_by=request.user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        ).distinct(),
    }
    return render(request, 'review/rc_dashboard.html', context)



@login_required
def osar_dashboard(request):
    if not request.user.groups.filter(name='OSAR').exists():
        return redirect('review:review_dashboard')
    
    context = {
        'osar_submissions': Submission.objects.all().select_related(
            'primary_investigator__userprofile',
            'study_type'
        ),
        'osar_reviews': ReviewRequest.objects.filter(
            Q(requested_to__groups__name='OSAR') | Q(requested_by__groups__name='OSAR'),
            Q(requested_to=request.user) | Q(requested_by=request.user)
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by',
            'requested_to'
        ).distinct(),
        'submission_status_choices': SUBMISSION_STATUS_CHOICES,
    }
    return render(request, 'review/osar_dashboard.html', context)

@login_required
def view_notepad(request, submission_id, notepad_type):
    # Verify permissions
    if not request.user.groups.filter(name=notepad_type).exists():
        messages.error(request, f"You don't have permission to view {notepad_type} notepad.")
        return redirect('review:review_dashboard')
    
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if request.method == 'POST':
        note_text = request.POST.get('note_text', '').strip()
        if note_text:
            NotepadEntry.objects.create(
                submission=submission,
                notepad_type=notepad_type,
                text=note_text,
                created_by=request.user
            )
            messages.success(request, 'Note added successfully.')
        return redirect('review:view_notepad', submission_id=submission_id, notepad_type=notepad_type)
    
    notes = NotepadEntry.objects.filter(
        submission=submission,
        notepad_type=notepad_type
    ).select_related('created_by')
    
    context = {
        'submission': submission,
        'notes': notes,
        'notepad_type': notepad_type
    }
    return render(request, 'review/view_notepad.html', context)