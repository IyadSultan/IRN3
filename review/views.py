######################
# Imports
######################
from datetime import datetime, timedelta
import json
import logging

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import (
    Q, Count, Avg, F, Prefetch
)
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView

from forms_builder.models import DynamicForm
from iRN.constants import SUBMISSION_STATUS_CHOICES
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
# Models
from submission.models import Submission, StudyAction  # Import StudyAction from submission.models
from .models import Review, ReviewRequest, NotepadEntry

# Utils
from users.utils import get_system_user
from .utils.notifications import send_irb_decision_notification
######################
# Review Dashboard
# URL: path('', ReviewDashboardView.as_view(), name='review_dashboard'),
######################



class ReviewDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'review/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get user groups
        is_osar = user.groups.filter(name='OSAR').exists()
        is_irb = user.groups.filter(name='IRB').exists()
        is_rc = user.groups.filter(name='RC').exists()

        # Determine group name for notepad
        group_name = 'OSAR' if is_osar else 'IRB' if is_irb else 'RC' if is_rc else 'general'

        # Base queryset for submissions
        base_submission_qs = Submission.objects.select_related(
            'primary_investigator__userprofile',
            'study_type'
        )

        # Filter submissions based on group
        if is_irb:
            submissions = base_submission_qs.filter(show_in_irb=True)
            review_filter = Q(requested_to__groups__name='IRB') | Q(requested_by__groups__name='IRB')
        elif is_rc:
            submissions = base_submission_qs.filter(show_in_rc=True)
            review_filter = Q(requested_to__groups__name='RC') | Q(requested_by__groups__name='RC')
        else:  # OSAR or other users
            submissions = base_submission_qs.all()
            review_filter = Q()

        # Prefetch review requests with filtering
        submissions = submissions.prefetch_related(
            Prefetch(
                'review_requests',
                queryset=ReviewRequest.objects.filter(review_filter).select_related(
                    'requested_to__userprofile',
                    'requested_by__userprofile'
                )
            )
        )

        # Get review requests based on group filter
        review_requests = ReviewRequest.objects.filter(review_filter) if review_filter else ReviewRequest.objects.all()

        # Get pending and completed reviews
        pending_reviews = review_requests.filter(
            requested_to=user,
            status__in=['pending', 'overdue', 'extended']
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by__userprofile'
        )

        completed_reviews = review_requests.filter(
            requested_to=user,
            status='completed'
        ).select_related(
            'submission__primary_investigator__userprofile',
            'requested_by__userprofile'
        )

        # Check for unread notes for each submission
        for submission in submissions:
            submission.has_unread_notes = NotepadEntry.objects.filter(
                submission=submission,
                notepad_type=group_name
            ).exclude(read_by=user).exists()

        context.update({
            'submissions': submissions,
            'is_osar': is_osar,
            'is_irb': is_irb,
            'is_rc': is_rc,
            'group_name': group_name,
            'review_requests': review_requests,
            'pending_reviews': pending_reviews,
            'completed_reviews': completed_reviews,
            'submission_status_choices': SUBMISSION_STATUS_CHOICES,
        })

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


class CreateReviewRequestView(LoginRequiredMixin, CreateView):
    model = ReviewRequest
    form_class = ReviewRequestForm
    template_name = 'review/create_review_request.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        if not ReviewRequest.can_create_review_request(request.user):
            raise PermissionDenied("You don't have permission to create review requests.")
        return super().dispatch(request, *args, **kwargs)

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
from django.shortcuts import render, get_object_or_404
from submission.models import Submission, VersionHistory


class ReviewSummaryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for displaying a comprehensive summary of a submission's reviews"""
    template_name = 'review/review_summary.html'

    def setup(self, request, *args, **kwargs):
        """Initialize common attributes used by multiple methods"""
        super().setup(request, *args, **kwargs)
        self.submission = get_object_or_404(Submission, pk=kwargs.get('submission_id'))
        self.is_osar = request.user.groups.filter(name='OSAR').exists()
        self.is_irb = request.user.groups.filter(name='IRB').exists()
        self.is_rc = request.user.groups.filter(name='RC').exists()

    def test_func(self):
        """Verify user permission to access the submission"""
        user = self.request.user
        
        # Check group permissions
        if user.groups.filter(name__in=['OSAR', 'IRB']).exists():
            return True

        # RC members can view submissions in their department
        if user.groups.filter(name='RC').exists():
            return user.userprofile.department == self.submission.primary_investigator.userprofile.department

        # Check direct involvement
        return any([
            user == self.submission.primary_investigator,
            self.submission.coinvestigators.filter(user=user).exists(),
            self.submission.research_assistants.filter(user=user).exists()
        ])

    def handle_no_permission(self):
        """Route users to appropriate dashboard when access is denied"""
        messages.error(self.request, "You don't have permission to view this submission's details.")
        
        if self.is_osar:
            return redirect('review:osar_dashboard')
        elif self.is_rc:
            return redirect('review:rc_dashboard')
        elif self.is_irb:
            return redirect('review:irb_dashboard')
        return redirect('submission:dashboard')

    def get_review_requests(self):
        """Get filtered review requests based on user group"""
        base_query = self.submission.review_requests.select_related(
            'requested_to__userprofile',
            'requested_by__userprofile'
        ).prefetch_related('review_set')

        if self.is_irb:
            return base_query.filter(
                Q(requested_to__groups__name='IRB') |
                Q(requested_by__groups__name='IRB')
            )
        elif self.is_rc:
            return base_query.filter(
                Q(requested_to__groups__name='RC') |
                Q(requested_by__groups__name='RC')
            )
        return base_query.all()

    def get_version_histories(self):
        """Get submission version history"""
        version_histories = list(self.submission.version_histories.all().order_by('-version'))
        for i, version in enumerate(version_histories):
            if i < len(version_histories) - 1:
                version.next_version = version_histories[i + 1].version
            else:
                version.next_version = None
        return version_histories

    def get_user_permissions(self, user):
        """Determine user-specific permissions"""
        return {
            'can_make_decision': self.is_irb,
            'can_download_pdf': True,
            'can_assign_irb': self.is_irb and not self.submission.khcc_number,
            'is_osar': self.is_osar,
            'is_rc': self.is_rc,
            'is_irb': self.is_irb,
            'can_create_review': any([
                user.groups.filter(name=role).exists() 
                for role in ['OSAR', 'IRB', 'RC']
            ])
        }

    def get_submission_stats(self, review_requests):
        """Calculate submission statistics"""
        submission_date = self.submission.date_submitted or timezone.now()
        days_since = (timezone.now().date() - submission_date.date()).days

        return {
            'total_reviews': review_requests.count(),
            'completed_reviews': review_requests.filter(status='completed').count(),
            'pending_reviews': review_requests.filter(status='pending').count(),
            'days_since_submission': max(0, days_since)
        }

    def prepare_context(self):
        """Prepare all context data"""
        review_requests = self.get_review_requests()
        user_permissions = self.get_user_permissions(self.request.user)
        version_histories = self.get_version_histories()

        # Get study actions
        actions = StudyAction.objects.filter(
            submission=self.submission
        ).select_related(
            'performed_by__userprofile'
        ).prefetch_related(
            'documents'
        ).order_by('-date_created')

        # Format actions for template
        formatted_actions = [{
            'id': action.id,
            'action_type': action.get_action_type_display(),
            'performed_by': action.performed_by.get_full_name(),
            'date_created': action.date_created.strftime('%Y-%m-%d %H:%M'),
            'status': action.status,
            'notes': action.notes,
            'pdf_url': reverse('submission:download_action_pdf', kwargs={
                'submission_id': self.submission.temporary_id,
                'action_id': action.id
            }) if action.documents.exists() else None
        } for action in actions]

        return {
            'submission': self.submission,
            'review_requests': review_requests,
            'version_histories': version_histories,
            'stats': self.get_submission_stats(review_requests),
            'has_active_reviews': review_requests.filter(
                status__in=['pending', 'in_progress']
            ).exists(),
            'has_reviews': review_requests.exists(),
            'study_actions': formatted_actions,
            'can_process_actions': self.request.user.groups.filter(
                name__in=['OSAR', 'IRB', 'RC']
            ).exists(),
            'is_osar': self.is_osar,
            'is_irb': self.is_irb,
            'is_rc': self.is_rc,
            **user_permissions
        }

    def get(self, request, *args, **kwargs):
        """Handle GET requests"""
        if not self.test_func():
            return self.handle_no_permission()
        return render(request, self.template_name, self.prepare_context())

    def post(self, request, *args, **kwargs):
        """Handle POST requests for submission decisions"""
        if not self.test_func():
            return self.handle_no_permission()

        action = request.POST.get('action')
        comments = request.POST.get('comments', '').strip()

        if not comments:
            messages.error(request, "Comments are required for making a decision.")
            return redirect('review:review_summary', submission_id=self.submission.pk)

        try:
            with transaction.atomic():
                # Update submission status and lock state
                if action == 'revision_requested':
                    self.submission.status = 'revision_requested'
                    self.submission.is_locked = False
                elif action in ['rejected', 'accepted']:
                    self.submission.status = action
                    self.submission.is_locked = True
                else:
                    messages.error(request, "Invalid action specified.")
                    return redirect('review:review_summary', submission_id=self.submission.pk)

                self.submission.save()
                send_irb_decision_notification(self.submission, action, comments)
                
                messages.success(
                    request,
                    f"Submission successfully marked as {action.replace('_', ' ').title()}"
                )
                
        except Exception as e:
            messages.error(request, f"Error processing decision: {str(e)}")
        
        return redirect('review:review_summary', submission_id=self.submission.pk)
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
    """
    View function to handle notepad operations (viewing and adding notes).
    Also handles marking notes as read automatically.
    """
    # Check user permissions
    if not request.user.groups.filter(name=notepad_type).exists():
        messages.error(request, f"You don't have permission to view {notepad_type} notepad.")
        return redirect('review:review_dashboard')
    
    # Get submission or return 404
    submission = get_object_or_404(
        Submission.objects.select_related('primary_investigator__userprofile'),
        pk=submission_id
    )
    
    try:
        # Handle POST request (adding new note)
        if request.method == 'POST':
            note_text = request.POST.get('note_text', '').strip()
            if note_text:
                with transaction.atomic():
                    # Create new note
                    note = NotepadEntry.objects.create(
                        submission=submission,
                        notepad_type=notepad_type,
                        text=note_text,
                        created_by=request.user
                    )
                    # Mark as read by creator
                    note.read_by.add(request.user)
                    messages.success(request, 'Note added successfully.')
            else:
                messages.warning(request, 'Note text cannot be empty.')
            return redirect('review:view_notepad', submission_id=submission_id, notepad_type=notepad_type)

        # Handle GET request (viewing notes)
        with transaction.atomic():
            # Get all notes with related data
            notes = NotepadEntry.objects.filter(
                submission=submission,
                notepad_type=notepad_type
            ).select_related(
                'created_by',
                'created_by__userprofile'
            ).prefetch_related(
                'read_by'
            ).order_by('-created_at')

            # Mark all unread notes as read
            unread_notes = notes.exclude(read_by=request.user)
            for note in unread_notes:
                note.read_by.add(request.user)

            # Prepare context
            context = {
                'submission': submission,
                'notes': notes,
                'notepad_type': notepad_type,
                'can_add_notes': True,  # You might want to add additional permission checks here
                'total_notes': notes.count(),
                'unread_count': unread_notes.count()
            }

            return render(request, 'review/view_notepad.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('review:review_dashboard')

# views.py
def has_unread_notes(submission_id, notepad_type, user):
    return NotepadEntry.objects.filter(
        submission_id=submission_id,
        notepad_type=notepad_type
    ).exclude(read_by=user).exists()

# In your dashboard view (ReviewDashboardView)
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Add check for unread notes for each submission
    for submission in context['submissions']:
        submission.has_unread_notes = has_unread_notes(
            submission.pk, 
            context['group_name'], 
            self.request.user
        )
    
    return context
# review/views.py
class ProcessSubmissionDecisionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'submission.change_submission_status'
    
    def post(self, request, submission_id):
        submission = get_object_or_404(Submission, pk=submission_id)
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        try:
            with transaction.atomic():
                if action == 'revision_requested':
                    submission.status = 'revision_requested'
                    submission.is_locked = False
                elif action == 'rejected':
                    submission.status = 'rejected'
                    submission.is_locked = True
                elif action == 'accepted':
                    submission.status = 'accepted'
                    submission.is_locked = True
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid action'
                    }, status=400)
                
                submission.save()
                
                # Send notification
                send_irb_decision_notification(submission, action, comments)
                
                messages.success(request, f"Submission successfully marked as {action.replace('_', ' ').title()}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Submission status updated to {action}',
                    'redirect_url': reverse('review:review_summary', args=[submission.pk])
                })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        


# review/views.py

from django.http import JsonResponse
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncMonth, ExtractDay
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import ReviewRequest, Review
from submission.models import Submission, CoInvestigator
from django.contrib.auth.models import User

@login_required
def get_dashboard_data(request):
    """API endpoint for dashboard data"""
    try:
        print("Starting dashboard data fetch...")
        # Calculate date ranges
        now = timezone.now()
        six_months_ago = now - timedelta(days=180)
        
        # Get submissions excluding drafts
        submissions = Submission.objects.exclude(status='draft')
        total_submissions = submissions.count()
        print(f"Total submissions: {total_submissions}")

        # Get active reviewers
        active_reviewers = ReviewRequest.objects.filter(
            status='pending'
        ).values('requested_to').distinct().count()
        print(f"Active reviewers: {active_reviewers}")

        # Get pending reviews
        pending_reviews = ReviewRequest.objects.filter(
            status='pending'
        ).count()
        print(f"Pending reviews: {pending_reviews}")

        # Calculate average review time
        avg_review_time = 0
        completed_reviews = ReviewRequest.objects.filter(status='completed')
        if completed_reviews.exists():
            avg_time = completed_reviews.aggregate(
                avg_time=Avg(F('updated_at') - F('created_at'))
            )['avg_time']
            if avg_time:
                avg_review_time = avg_time.days
        print(f"Average review time: {avg_review_time}")

        # Get monthly submissions trend
        submission_trends = []
        monthly_data = submissions.filter(
            date_submitted__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date_submitted')
        ).values('month').annotate(
            count=Count('temporary_id')
        ).order_by('month')
        
        for item in monthly_data:
            if item['month']:
                submission_trends.append({
                    'month': item['month'].strftime('%b %Y'),
                    'count': item['count']
                })
        print(f"Submission trends: {len(submission_trends)} months")

        # Get status distribution
        status_dist = submissions.values('status').annotate(
            count=Count('temporary_id')
        ).order_by('-count')
        
        status_distribution = [{
            'status': item['status'].replace('_', ' ').title(),
            'count': item['count']
        } for item in status_dist]
        print(f"Status distribution: {len(status_distribution)} statuses")

        # Get institution distribution
        institution_dist = submissions.select_related(
            'primary_investigator__userprofile'
        ).values(
            'primary_investigator__userprofile__institution'
        ).annotate(
            count=Count('temporary_id')
        ).order_by('-count')

        institutions = [{
            'name': item['primary_investigator__userprofile__institution'] or 'Unknown',
            'count': item['count']
        } for item in institution_dist]
        print(f"Institutions: {len(institutions)} institutions")

        # Get roles distribution
        role_dist = submissions.select_related(
            'primary_investigator__userprofile'
        ).values(
            'primary_investigator__userprofile__role'
        ).annotate(
            count=Count('temporary_id')
        ).order_by('-count')

        role_distribution = [{
            'role': item['primary_investigator__userprofile__role'] or 'Unknown',
            'count': item['count']
        } for item in role_dist]
        print(f"Roles: {len(role_distribution)} roles")

        # Calculate IRB and RC review times
        irb_avg_time = 0
        irb_reviews = ReviewRequest.objects.filter(
            requested_to__groups__name='IRB',
            status='completed'
        )
        if irb_reviews.exists():
            irb_time = irb_reviews.aggregate(
                avg_time=Avg(F('updated_at') - F('created_at'))
            )['avg_time']
            if irb_time:
                irb_avg_time = irb_time.days

        rc_avg_time = 0
        rc_reviews = ReviewRequest.objects.filter(
            requested_to__groups__name='RC',
            status='completed'
        )
        if rc_reviews.exists():
            rc_time = rc_reviews.aggregate(
                avg_time=Avg(F('updated_at') - F('created_at'))
            )['avg_time']
            if rc_time:
                rc_avg_time = rc_time.days

        print(f"IRB avg time: {irb_avg_time}, RC avg time: {rc_avg_time}")

        # Get review time distributions
        irb_time_dist = {}
        for review in irb_reviews:
            days = (review.updated_at - review.created_at).days
            irb_time_dist[days] = irb_time_dist.get(days, 0) + 1

        rc_time_dist = {}
        for review in rc_reviews:
            days = (review.updated_at - review.created_at).days
            rc_time_dist[days] = rc_time_dist.get(days, 0) + 1

        response_data = {
            'totalSubmissions': total_submissions,
            'activeReviewers': active_reviewers,
            'avgReviewTime': avg_review_time,
            'pendingReviews': pending_reviews,
            'irbAvgTime': irb_avg_time,
            'rcAvgTime': rc_avg_time,
            'submissionTrends': submission_trends,
            'roleDistribution': role_distribution,
            'institutions': institutions,
            'statusDistribution': status_distribution,
            'irbTimeDistribution': [
                {'days': days, 'count': count}
                for days, count in sorted(irb_time_dist.items())
            ],
            'rcTimeDistribution': [
                {'days': days, 'count': count}
                for days, count in sorted(rc_time_dist.items())
            ]
        }

        print("Sending response data")
        return JsonResponse(response_data)

    except Exception as e:
        import traceback
        print(f"Error in dashboard data: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'submissionTrends': [],
            'statusDistribution': [],
            'roleDistribution': [],
            'institutions': [],
            'irbTimeDistribution': [],
            'rcTimeDistribution': [],
            'totalSubmissions': 0,
            'activeReviewers': 0,
            'avgReviewTime': 0,
            'pendingReviews': 0,
            'irbAvgTime': 0,
            'rcAvgTime': 0
        }, status=500)# review/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse

class QualityDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'review/dashboard/quality_dashboard.html'

    def test_func(self):
        return self.request.user.groups.filter(
            name__in=['OSAR', 'IRB', 'RC']
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Quality Dashboard',
        })
        return context
    def handle_no_permission(self):
        messages.error(
            self.request, 
            "You don't have permission to view the Quality Dashboard."
        )
        return redirect('review:review_dashboard')

@login_required
def check_notes_status(request, submission_id, notepad_type):
    """API endpoint to check for unread notes"""
    print(f"Debug: checking notes for submission {submission_id} and type {notepad_type}")  # Add this
    try:
        unread_notes = NotepadEntry.objects.filter(
            submission_id=submission_id,
            notepad_type=notepad_type
        ).exclude(read_by=request.user).exists()
        
        print(f"Debug: found unread notes: {unread_notes}")  # Add this
        
        response_data = {
            'hasNewNotes': unread_notes,
            'submissionId': submission_id,
            'notepadType': notepad_type
        }
        print(f"Debug: sending response: {response_data}")  # Add this
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Debug: Error occurred: {str(e)}")  # Add this
        return JsonResponse({
            'error': str(e)
        }, status=500)
    


@login_required 
def process_action(request, submission_id, action_id):
    """Process a study action (approve/reject) with custom message"""
    submission = get_object_or_404(Submission, pk=submission_id)
    action = get_object_or_404(StudyAction, pk=action_id, submission=submission)

    if not request.user.groups.filter(name__in=['OSAR', 'IRB', 'RC']).exists():
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to process actions'
        }, status=403)

    if request.method == 'POST':
        try:
            decision = request.POST.get('decision')
            comments = request.POST.get('comments', '').strip()
            letter_text = request.POST.get('letter_text', '').strip()
            
            if not comments or not letter_text:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Both comments and letter text are required'
                }, status=400)

            with transaction.atomic():
                # Update action status
                action.status = 'completed' if decision == 'approve' else 'cancelled'
                action.notes = comments
                action.save()

                # Get notification recipients
                recipients = [action.performed_by]  # Person who submitted the action
                if action.performed_by != submission.primary_investigator:
                    recipients.append(submission.primary_investigator)

                # Create notification with customized letter
                message = Message.objects.create(
                    sender=get_system_user(),
                    subject=f'Study Action {decision.title()}d - {submission.title}',
                    body=f"""
Dear {action.performed_by.get_full_name()},

Regarding your {action.get_action_type_display()} request for submission "{submission.title}":

{letter_text}

Additional Comments from Reviewer:
{comments}

Action Details:
- Submission ID: {submission.temporary_id}
- Action Type: {action.get_action_type_display()}
- Decision: {decision.title()}
- Processed by: {request.user.get_full_name()}
- Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Best regards,
{request.user.get_full_name()}
                    """.strip(),
                    related_submission=submission,
                    message_type='decision'
                )
                
                # Add recipients
                for recipient in recipients:
                    message.recipients.add(recipient)

                # If action was approved, process necessary changes
                if decision == 'approve':
                    if action.action_type == 'closure':
                        submission.status = 'closed'
                        submission.is_locked = True
                    elif action.action_type == 'withdrawal':
                        submission.status = 'withdrawn'
                        submission.is_locked = True
                    submission.save()

                return JsonResponse({
                    'status': 'success',
                    'message': f'Action {decision}d successfully'
                })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)



def generate_action_pdf(action, as_buffer=False):
    """Generate PDF for a study action"""
    try:
        logger.info(f"Generating PDF for action {action.id}")
        
        buffer = BytesIO()
        pdf_generator = PDFGenerator(buffer, action.submission, action.version, action.performed_by)
        
        # Add basic submission info
        pdf_generator.add_header()
        pdf_generator.add_basic_info()
        
        # Add action details
        pdf_generator.add_study_action_details(action)
        
        # Add form responses
        pdf_generator.add_dynamic_forms()
        
        # Add footer
        pdf_generator.add_footer()
        pdf_generator.canvas.save()
        
        if as_buffer:
            buffer.seek(0)
            return buffer
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"study_action_{action.get_action_type_display()}_{action.date_created.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
            
    except Exception as e:
        logger.error(f"Error generating action PDF: {str(e)}")
        logger.error("PDF generation error details:", exc_info=True)
        return None
    

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from submission.models import StudyAction
from .utils.pdf_generator import generate_action_pdf

@login_required
def download_action_pdf(request, action_id):
    """
    View function to generate and download a PDF for a study action.
    """
    # Get the action or return 404
    action = get_object_or_404(StudyAction, pk=action_id)
    
    # Check if user has permission to view this action
    if not request.user.groups.filter(name__in=['OSAR', 'IRB', 'RC']).exists():
        return HttpResponse('Permission denied', status=403)
    
    # Generate the PDF
    pdf_response = generate_action_pdf(action)
    
    if pdf_response is None:
        return HttpResponse('Error generating PDF', status=500)
    
    return pdf_response

