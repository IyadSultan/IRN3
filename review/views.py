######################
# Imports
######################

from datetime import timedelta
import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, FormView
from django import forms
from django.http import HttpResponse
from django.utils.text import slugify
from datetime import datetime
from django.core.files.base import ContentFile
from messaging.models import Message, MessageAttachment
from users.utils import get_system_user

from .forms import ReviewRequestForm
from .models import ReviewRequest, Review, FormResponse
from .utils.notifications import send_review_request_notification
from forms_builder.models import DynamicForm
from messaging.models import Message
from submission.models import Submission
from users.utils import get_system_user
from .utils.pdf_generator import generate_review_pdf
from submission.utils.pdf_generator import PDFGenerator, generate_submission_pdf



######################
# Review Dashboard
# URL: path('', ReviewDashboardView.as_view(), name='review_dashboard'),
######################

class ReviewDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'review/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get submissions needing review (for OSAR Coordinators)
        if user.groups.filter(name='OSAR Coordinator').exists():
            submissions_needing_review = Submission.objects.filter(
                status='submitted'
            ).exclude(
                review_requests__isnull=False
            ).select_related(
                'primary_investigator__userprofile',
                'study_type'
            )
            context['submissions_needing_review'] = submissions_needing_review

        # Get pending reviews where user is the reviewer
        pending_reviews = ReviewRequest.objects.select_related(
            'submission__primary_investigator__userprofile',
            'submission__study_type',
            'requested_by',
            'requested_to'
        ).filter(
            requested_to=user,
            status__in=['pending', 'overdue', 'extended']
        ).order_by('-created_at')
        context['pending_reviews'] = pending_reviews

        # Get completed reviews
        completed_reviews = ReviewRequest.objects.select_related(
            'submission__primary_investigator__userprofile',
            'submission__study_type',
            'requested_by',
            'requested_to'
        ).filter(
            requested_to=user,
            status='completed'
        ).order_by('-updated_at')
        context['completed_reviews'] = completed_reviews

        return context


######################
# Create Review Request
# URL: path('create/<int:submission_id>/', CreateReviewRequestView.as_view(), name='create_review_request'),
######################

class CreateReviewRequestView(LoginRequiredMixin, FormView):
    template_name = 'review/create_review_request.html'
    form_class = ReviewRequestForm

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['deadline'] = timezone.now().date() + timedelta(days=14)
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['study_type'] = self.submission.study_type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submission'] = self.submission
        return context

    def form_valid(self, form):
        review_request = form.save(commit=False)
        review_request.submission = self.submission
        review_request.requested_by = self.request.user
        review_request.status = 'pending'
        review_request.submission_version = self.submission.version
        review_request.save()
        form.save_m2m()

        send_review_request_notification(review_request)
        messages.success(self.request, 'Review request created successfully.')
        return redirect('review:review_dashboard')


######################
# Decline Review
# URL: path('review/<int:review_id>/decline/', DeclineReviewView.as_view(), name='decline_review'),
######################

class DeclineReviewView(LoginRequiredMixin, View):
    template_name = 'review/decline_review.html'

    def get(self, request, review_id):
        review_request = self.get_review_request(review_id, request.user)
        if not review_request:
            return redirect('review:review_dashboard')
        return render(request, self.template_name, {'review_request': review_request})

    def post(self, request, review_id):
        review_request = self.get_review_request(review_id, request.user)
        if not review_request:
            return redirect('review:review_dashboard')

        reason = request.POST.get('reason')
        if not reason:
            messages.error(request, "Please provide a reason for declining the review.")
            return redirect('review:decline_review', review_id=review_id)

        try:
            with transaction.atomic():
                review_request.status = 'declined'
                review_request.conflict_of_interest_declared = True
                review_request.conflict_of_interest_details = reason
                review_request.save()

                system_user = get_system_user()
                message = Message.objects.create(
                    sender=system_user,
                    subject=f'Review Request Declined - {review_request.submission.title}',
                    body=render_to_string('review/decline_notification_email.txt', {
                        'requested_by': review_request.requested_by.userprofile.full_name,
                        'submission_title': review_request.submission.title,
                        'decliner': request.user.userprofile.full_name,
                        'reason': reason,
                    }),
                    study_name=review_request.submission.title,
                    related_submission=review_request.submission
                )
                message.recipients.add(review_request.requested_by)

                messages.success(request, "Review request declined successfully.")
                return redirect('review:review_dashboard')
        except Exception as e:
            messages.error(request, f"Error declining review: {str(e)}")
            return redirect('review:decline_review', review_id=review_id)

    def get_review_request(self, review_id, user):
        review_request = get_object_or_404(ReviewRequest, pk=review_id)
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

    def dispatch(self, request, *args, **kwargs):
        self.review_request = get_object_or_404(ReviewRequest, pk=kwargs['review_id'])
        if not self.has_permission(request.user, self.review_request):
            messages.error(request, "You don't have permission to request an extension for this review.")
            return redirect('review:review_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, user, review_request):
        return user == review_request.requested_to and review_request.status == 'pending'

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
            extension_days = (new_deadline_date - self.review_request.deadline).days

            with transaction.atomic():
                message = Message.objects.create(
                    sender=request.user,
                    subject=f'Extension Request for Review #{self.review_request.id}',
                    body=f"""
Extension Request Details:
-------------------------
Review: {self.review_request.submission.title}
Current Deadline: {self.review_request.deadline}
Requested New Deadline: {new_deadline_date}
Extension Days: {extension_days} days
Reason: {reason}

Please review this request and respond accordingly.
                    """.strip(),
                    study_name=self.review_request.submission.title,
                    related_submission=self.review_request.submission
                )
                message.recipients.add(self.review_request.requested_by)

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

                    # Generate PDF
                    pdf_buffer = generate_review_pdf(review, self.review_request.submission, review.formresponse_set.all())
                    
                    if pdf_buffer:
                        # Create notification message with PDF attachment
                        submission_title = self.review_request.submission.title
                        reviewer_name = request.user.get_full_name()
                        
                        message = Message.objects.create(
                            sender=get_system_user(),
                            subject=f'Review Completed - {submission_title}',
                            body=f"""
Dear {self.review_request.requested_by.userprofile.full_name},

A review has been completed for This submission.

Submission: {submission_title}
Reviewer: {reviewer_name}
Date Completed: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please find the detailed review report attached to this message.

Best regards,
iRN System
                            """.strip(),
                            study_name=submission_title,
                            related_submission=self.review_request.submission
                        )
                        
                        # Add recipients
                        message.recipients.add(self.review_request.requested_by)
                        
                        # Add CC recipients
                        message.cc.add(self.review_request.requested_to)  # Add reviewer to CC
                        
                      
                        # Create PDF attachment
                        submission_title_slug = slugify(submission_title)
                        reviewer_name_slug = slugify(reviewer_name)
                        date_str = timezone.now().strftime('%Y_%m_%d')
                        filename = f"review_{submission_title_slug}_{reviewer_name_slug}_{date_str}.pdf"
                        
                        MessageAttachment.objects.create(
                            message=message,
                            file=ContentFile(pdf_buffer.getvalue(), name=filename),
                            filename=filename
                        )
                        
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

class ReviewSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'review/review_summary.html'

    def dispatch(self, request, *args, **kwargs):
        self.submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
        if not self.has_permission(request.user, self.submission):
            messages.error(request, "You don't have permission to view this review summary.")
            return redirect('submission:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, user, submission):
        return user == submission.primary_investigator or \
               user.groups.filter(name='IRB Coordinator').exists() or \
               submission.review_requests.filter(requested_by=user).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = Review.objects.filter(
            submission=self.submission
        ).select_related(
            'reviewer__userprofile',
            'review_request'
        ).prefetch_related(
            'formresponse_set__form'
        ).order_by('date_submitted')

        context.update({
            'submission': self.submission,
            'reviews': reviews,
            'can_make_decision': self.request.user.groups.filter(name='IRB Coordinator').exists()
        })
        return context


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
                # Assume VersionHistory model and generate_irb_number function exist
                # VersionHistory.objects.create(...)
                # if decision == 'approved' and not self.submission.irb_number:
                #     self.submission.irb_number = generate_irb_number(self.submission)
                #     self.submission.save()

                system_user = get_system_user()
                message = Message.objects.create(
                    sender=system_user,
                    subject=f'IRB Decision - {self.submission.title}',
                    body=f"""
Dear {self.submission.primary_investigator.userprofile.full_name},

The IRB has made a decision regarding your submission "{self.submission.title}".

Decision: {decision.replace('_', ' ').title()}

{comments if comments else ''}

{'Please review the comments and submit a revised version.' if decision == 'revision_required' else ''}

Best regards,
AIDI System
                    """.strip(),
                    study_name=self.submission.title,
                    related_submission=self.submission
                )
                message.recipients.add(self.submission.primary_investigator)

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
