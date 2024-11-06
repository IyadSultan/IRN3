# review/admin.py

from django.contrib import admin
from .models import ReviewRequest, Review, FormResponse

@admin.register(ReviewRequest)
class ReviewRequestAdmin(admin.ModelAdmin):
    list_display = ('submission', 'requested_by', 'requested_to', 'status', 'deadline')
    list_filter = ('status',)
    search_fields = ('submission__title', 'requested_by__username', 'requested_to__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer', 'date_submitted')
    search_fields = ('submission__title', 'reviewer__username')

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'review', 'date_submitted')
    search_fields = ('form__title', 'review__reviewer__username')
# review/apps.py

from django.apps import AppConfig


class ReviewConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "review"
import os

# try to remove combined.py if it exists
if os.path.exists('combined.py'):
    os.remove('combined.py')

app_directory = "../review/"
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/review'

# List all HTML files in the directory
html_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

# Open the output file in append mode to avoid overwriting existing content
with open(output_file, 'a') as outfile:
    for fname in html_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)# review/forms.py

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ReviewRequest
from forms_builder.models import DynamicForm
from dal import autocomplete

from django import forms
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import ReviewRequest
from forms_builder.models import DynamicForm
from dal import autocomplete

class ReviewRequestForm(forms.ModelForm):
    requested_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-placeholder': 'Select a reviewer...',
        }),
        label="Select Reviewer",
        help_text="Choose a qualified reviewer for this submission"
    )

    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'deadline', 'message', 'selected_forms']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, study_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get relevant reviewer groups
        reviewer_groups = set(['IRB Member', 'Research Council Member', 'AHARPP Reviewer'])
        
        if study_type:
            reviewer_groups = set()
            try:
                if getattr(study_type, 'requires_irb', True):
                    reviewer_groups.add('IRB Member')
                if getattr(study_type, 'requires_research_council', True):
                    reviewer_groups.add('Research Council Member')
                if getattr(study_type, 'requires_aharpp', True):
                    reviewer_groups.add('AHARPP Reviewer')
            except AttributeError:
                # If attributes don't exist, include all reviewer groups
                reviewer_groups = set(['IRB Member', 'Research Council Member', 'AHARPP Reviewer'])
        
        # Filter reviewers based on group membership
        reviewers = User.objects.filter(
            groups__name__in=reviewer_groups,
            is_active=True
        ).distinct().select_related(
            'userprofile'
        ).order_by(
            'userprofile__full_name'
        )
        
        # Update the queryset for requested_to field
        self.fields['requested_to'].queryset = reviewers
        
        # Add user full names to the display
        self.fields['requested_to'].label_from_instance = lambda user: (
            f"{user.get_full_name() or user.username} "
            f"({', '.join(user.groups.values_list('name', flat=True))})"
        )

        # Get all available forms
        form_queryset = DynamicForm.objects.all().order_by('name')
        self.fields['selected_forms'].queryset = form_queryset

class ConflictOfInterestForm(forms.Form):
    conflict_of_interest = forms.ChoiceField(
        choices=[('no', 'No'), ('yes', 'Yes')],
        widget=forms.RadioSelect,
        label='Do you have a conflict of interest with this submission?'
    )
    conflict_details = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Provide details (optional)'}),
        required=False,
        label='Conflict Details'
    )
from django.db import models
from django.contrib.auth.models import User
from submission.models import Submission, get_status_choices
from forms_builder.models import DynamicForm
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
from django.apps import apps

def get_status_choices():
    """Get status choices for review requests."""
    DEFAULT_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('reviews_completed', 'Reviews Completed'),
    ]
    
    try:
        choices = cache.get('review_status_choices')
        if not choices:
            StatusChoice = apps.get_model('review', 'StatusChoice')
            choices = list(StatusChoice.objects.filter(is_active=True).values_list('code', 'label'))
            if choices:
                cache.set('review_status_choices', choices)
        return choices or DEFAULT_CHOICES
    except Exception:
        return DEFAULT_CHOICES

class StatusChoice(models.Model):
    """Model to store custom status choices."""
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Status Choice'
        verbose_name_plural = 'Status Choices'

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete('review_status_choices')



class ReviewRequest(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE,  related_name='review_requests' )
    submission_version = models.PositiveIntegerField(
        help_text="Version number of the submission being reviewed"
    )
    requested_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='review_requests_created'
    )
    requested_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='review_requests_received'
    )
    message = models.TextField(blank=True)
    deadline = models.DateField()
    status = models.CharField(
        max_length=50,
        choices=get_status_choices,
        default='pending'
    )
    selected_forms = models.ManyToManyField(DynamicForm)
    conflict_of_interest_declared = models.BooleanField(null=True)
    conflict_of_interest_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=1)
    extension_requested = models.BooleanField(default=False)
    proposed_deadline = models.DateField(null=True, blank=True)
    extension_reason = models.TextField(null=True, blank=True)
    
    parent_request = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='child_requests'
    )
    forwarding_chain = models.JSONField(
        default=list,
        help_text="List of users who forwarded this request"
    )
    can_forward = models.BooleanField(
        default=False,
        help_text="Whether this reviewer can forward to others"
    )

    @property
    def is_overdue(self):
        return self.deadline < timezone.now().date()

    @property
    def days_until_deadline(self):
        return (self.deadline - timezone.now().date()).days

    def save(self, *args, **kwargs):
        # Ensure submission_version is an integer
        if isinstance(self.submission_version, datetime):
            self.submission_version = self.submission.version
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review Request for {self.submission} (Version {self.submission_version})"

class Review(models.Model):
    review_request = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    submission_version = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.reviewer} for {self.submission}"

class FormResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    form = models.ForeignKey('forms_builder.DynamicForm', on_delete=models.CASCADE)
    response_data = models.JSONField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.form} for {self.review}"




# tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_review_reminders():
    upcoming_deadlines = ReviewRequest.objects.filter(
        status='pending',
        deadline__lte=timezone.now() + timedelta(days=2)
    )
    for request in upcoming_deadlines:
        send_reminder_email(request)from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from django.utils import timezone
from datetime import timedelta
from submission.models import Submission, VersionHistory
from forms_builder.models import DynamicForm, StudyType
from review.models import ReviewRequest, Review, FormResponse
from review.forms import ReviewRequestForm, ConflictOfInterestForm

class ReviewTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.pi_user = User.objects.create_user('pi', 'pi@test.com', 'password123')
        
        # Create IRB Member group and add reviewer
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        
        # Add necessary permissions
        review_permission = Permission.objects.get(codename='can_create_review_request')
        self.admin_user.user_permissions.add(review_permission)
        
        # Create test study type
        self.study_type = StudyType.objects.create(name='Test Study')
        
        # Create test submission
        self.submission = Submission.objects.create(
            title='Test Submission',
            primary_investigator=self.pi_user,
            study_type=self.study_type,
            status='submitted',
            version=1
        )
        
        # Create version history
        VersionHistory.objects.create(
            submission=self.submission,
            version=1,
            status='submitted',
            date=timezone.now()
        )
        
        # Create test form
        self.test_form = DynamicForm.objects.create(
            name='Test Review Form',
            description='Test form for reviews'
        )

    def test_create_review_request(self):
        """Test creating a new review request"""
        self.client.login(username='admin', password='password123')
        
        data = {
            'requested_to': self.reviewer.id,
            'message': 'Please review this submission',
            'deadline': (timezone.now() + timedelta(days=7)).date(),
            'selected_forms': [self.test_form.id],
            'submission_version': 1
        }
        
        response = self.client.post(
            reverse('review:create_review_request', args=[self.submission.pk]),
            data
        )
        
        self.assertEqual(ReviewRequest.objects.count(), 1)
        review_request = ReviewRequest.objects.first()
        self.assertEqual(review_request.submission_version, 1)
        self.assertEqual(review_request.requested_to, self.reviewer)

    def test_submit_review(self):
        """Test submitting a review"""
        self.client.login(username='reviewer', password='password123')
        
        # Create review request
        review_request = ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            deadline=timezone.now() + timedelta(days=7)
        )
        review_request.selected_forms.add(self.test_form)
        
        # Submit conflict of interest form
        coi_data = {
            'conflict_of_interest': 'no'
        }
        response = self.client.post(
            reverse('review:submit_review', args=[review_request.id]),
            coi_data
        )
        
        # Verify COI response
        review_request.refresh_from_db()
        self.assertFalse(review_request.conflict_of_interest_declared)

    def test_review_dashboard(self):
        """Test review dashboard view"""
        self.client.login(username='reviewer', password='password123')
        
        # Create some review requests
        ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            status='pending',
            deadline=timezone.now() + timedelta(days=7)
        )
        
        response = self.client.get(reverse('review:review_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pending_reviews']), 1)

    def test_version_tracking(self):
        """Test version tracking in review process"""
        self.client.login(username='admin', password='password123')
        
        # Create review request for version 1
        review_request = ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            deadline=timezone.now() + timedelta(days=7)
        )
        
        # Update submission to version 2
        self.submission.increment_version()
        self.submission.refresh_from_db()
        
        # Verify version mismatch detection
        self.assertNotEqual(review_request.submission_version, self.submission.version)

    def test_permissions(self):
        """Test permission requirements for review functions"""
        # Test without login
        response = self.client.get(reverse('review:review_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with regular user
        regular_user = User.objects.create_user('regular', 'regular@test.com', 'password123')
        self.client.login(username='regular', password='password123')
        
        response = self.client.post(
            reverse('review:create_review_request', args=[self.submission.pk]),
            {}
        )
        self.assertEqual(response.status_code, 403)  # Permission denied

class ReviewFormTests(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        self.test_form = DynamicForm.objects.create(
            name='Test Form',
            description='Test form'
        )

    def test_review_request_form(self):
        """Test ReviewRequestForm validation"""
        form_data = {
            'requested_to': self.reviewer.id,
            'message': 'Please review',
            'deadline': (timezone.now() + timedelta(days=7)).date(),
            'selected_forms': [self.test_form.id],
            'submission_version': 1
        }
        
        form = ReviewRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_conflict_of_interest_form(self):
        """Test ConflictOfInterestForm validation"""
        # Test 'no' conflict
        form = ConflictOfInterestForm({'conflict_of_interest': 'no'})
        self.assertTrue(form.is_valid())
        
        # Test 'yes' conflict without details
        form = ConflictOfInterestForm({'conflict_of_interest': 'yes'})
        self.assertFalse(form.is_valid())
        
        # Test 'yes' conflict with details
        form = ConflictOfInterestForm({
            'conflict_of_interest': 'yes',
            'conflict_details': 'I have worked with the PI before'
        })
        self.assertTrue(form.is_valid())
# review/urls.py

from django.urls import path
from . import views
from submission.views import user_autocomplete


app_name = 'review'

urlpatterns = [
    path('', views.review_dashboard, name='review_dashboard'),
    path('create/<int:submission_id>/', views.create_review_request, name='create_review_request'),
    path('submit/<int:review_request_id>/', views.submit_review, name='submit_review'),
    path('dashboard/', views.review_dashboard, name='review_dashboard'),
    path('review/<int:review_id>/', views.view_review, name='view_review'),
    path('review/<int:review_id>/submit/', views.submit_review, name='submit_review'),
    path('review/<int:review_id>/extension/', views.request_extension, name='request_extension'),
    path('review/<int:review_id>/decline/', views.decline_review, name='decline_review'),
    path('submission/<int:submission_id>/summary/', views.review_summary, name='review_summary'),
    path('submission/<int:submission_id>/decision/', views.process_irb_decision, name='process_decision'),
    path('user-autocomplete/', user_autocomplete, name='user-autocomplete'),
]# review/utils.py

from messaging.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

def send_review_request_notification(review_request):
    sender = review_request.requested_by
    recipient = review_request.requested_to
    submission = review_request.submission
    subject = f"Review Request for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    You have been requested to review the submission titled '{submission.title}' (Version {submission.version}).

    Please log in to the system to proceed with the review.

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_conflict_of_interest_notification(review_request):
    sender = review_request.requested_to  # The reviewer who declared conflict
    recipient = review_request.requested_by  # The person who requested the review
    submission = review_request.submission
    subject = f"Conflict of Interest Declared for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    The reviewer {sender.get_full_name()} has declared a conflict of interest for the submission titled '{submission.title}'.

    Please assign a new reviewer.

    Conflict Details:
    {review_request.conflict_of_interest_details or 'No additional details provided.'}

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()


def send_review_completion_notification(review_request):
    sender = review_request.requested_to  # The reviewer
    recipient = review_request.requested_by  # The person who requested the review
    submission = review_request.submission
    subject = f"Review Completed for '{submission.title}'"
    body = f"""
    Dear {recipient.get_full_name()},

    The review for the submission titled '{submission.title}' has been completed by {sender.get_full_name()}.

    You can view the review by logging into the system.

    Thank you,
    {sender.get_full_name()}
    """

    # Create the message
    message = Message.objects.create(
        sender=sender,
        subject=subject.strip(),
        body=body.strip(),
        related_submission=submission,
    )
    # Add the recipient
    message.recipients.add(recipient)
    message.save()
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
    
    if request.method == 'POST':
        form = ReviewRequestForm(
            request.POST, 
            study_type=submission.study_type
        )
        if form.is_valid():
            review_request = form.save(commit=False)
            review_request.submission = submission
            review_request.requested_by = request.user
            review_request.submission_version = submission.version
            review_request.save()
            form.save_m2m()
            messages.success(request, 'Review request created successfully.')
            return redirect('review:review_dashboard')
    else:
        initial_data = {
            'deadline': timezone.now().date() + timezone.timedelta(days=14),
        }
        form = ReviewRequestForm(
            initial=initial_data,
            study_type=submission.study_type  # Make sure to pass study_type here
        )

    context = {
        'form': form,
        'submission': submission,
    }
    return render(request, 'review/create_review_request.html', context)




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
<!-- review/templates/review/create_review_request.html -->
{% extends 'base.html' %}
{% block content %}
<h2>Create Review Request for "{{ submission.title }}" (Version {{ submission.version }})</h2>
<form method="post">
    {% csrf_token %}
    {{ form.non_field_errors }}

    <div class="form-group">
        {{ form.requested_to.label_tag }}
        {{ form.requested_to }}
        {{ form.requested_to.errors }}
        <small class="form-text text-muted">{{ form.requested_to.help_text }}</small>
    </div>

    <div class="form-group">
        {{ form.deadline.label_tag }}
        {{ form.deadline }}
        {{ form.deadline.errors }}
        <small class="form-text text-muted">{{ form.deadline.help_text }}</small>
    </div>

    <div class="form-group">
        {{ form.message.label_tag }}
        {{ form.message }}
        {{ form.message.errors }}
        <small class="form-text text-muted">{{ form.message.help_text }}</small>
    </div>

    <div class="form-group">
        {{ form.selected_forms.label_tag }}
        {{ form.selected_forms }}
        {{ form.selected_forms.errors }}
        <small class="form-text text-muted">{{ form.selected_forms.help_text }}</small>
    </div>

    <button type="submit" class="btn btn-primary">Send Review Request</button>
</form>
{% endblock %}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Review Dashboard{% endblock %}

{% block page_specific_css %}
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/2.2.3/css/buttons.bootstrap4.min.css">
<style>
    .status-badge {
        padding: 0.4em 0.8em;
        border-radius: 0.25rem;
        font-size: 0.875em;
    }
    .status-pending { background-color: #ffc107; color: #000; }
    .status-accepted { background-color: #17a2b8; color: #fff; }
    .status-completed { background-color: #28a745; color: #fff; }
    .status-overdue { background-color: #dc3545; color: #fff; }
    
    .days-remaining {
        font-weight: bold;
    }
    .days-warning { color: #ffc107; }
    .days-danger { color: #dc3545; }
    .days-safe { color: #28a745; }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid mt-4">
    <h1 class="mb-4">Review Dashboard</h1>

    <!-- Filters -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">
                <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#filterCollapse">
                    <i class="fas fa-filter"></i> Filters
                </button>
            </h5>
        </div>
        <div id="filterCollapse" class="collapse show">
            <div class="card-body">
                <form id="filterForm" class="row g-3">
                    <div class="col-md-3">
                        <label for="status">Status</label>
                        <select id="status" class="form-select">
                            <option value="">All</option>
                            {% for status in status_choices %}
                            <option value="{{ status.0 }}">{{ status.1 }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label for="study_type">Study Type</label>
                        <select id="study_type" class="form-select">
                            <option value="">All</option>
                            {% for type in study_types %}
                            <option value="{{ type.id }}">{{ type.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label for="date_from">From Date</label>
                        <input type="date" id="date_from" class="form-control">
                    </div>
                    <div class="col-md-3">
                        <label for="date_to">To Date</label>
                        <input type="date" id="date_to" class="form-control">
                    </div>
                    <div class="col-12">
                        <button type="button" id="applyFilters" class="btn btn-primary">Apply Filters</button>
                        <button type="button" id="resetFilters" class="btn btn-secondary">Reset</button>
                        <button type="button" id="exportPDF" class="btn btn-success float-end">
                            <i class="fas fa-file-pdf"></i> Export to PDF
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    {% if submissions_needing_review %}
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Submissions Needing Review</h5>
        </div>
        <div class="card-body">
            <table class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Primary Investigator</th>
                        <th>Study Type</th>
                        <th>Submitted On</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for submission in submissions_needing_review %}
                    <tr>
                        <td>{{ submission.title }}</td>
                        <td>{{ submission.primary_investigator.userprofile.full_name }}</td>
                        <td>{{ submission.study_type.name }}</td>
                        <td>{{ submission.date_submitted|date:"M d, Y" }}</td>
                        <td>
                            <a href="{% url 'review:create_review_request' submission.pk %}" class="btn btn-sm btn-primary">
                                <i class="fas fa-plus"></i> Create Review Request
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Pending Reviews Table -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Pending Reviews</h5>
        </div>
        <div class="card-body">
            <table id="pendingReviewsTable" class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Primary Investigator</th>
                        <th>Study Type</th>
                        <th>Deadline</th>
                        <th>Status</th>
                        <th>Days Remaining</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- DataTables will populate this -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- Completed Reviews Table -->
    <div class="card">
        <div class="card-header">
            <h5 class="mb-0">Completed Reviews</h5>
        </div>
        <div class="card-body">
            <table id="completedReviewsTable" class="table table-striped table-bordered">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Primary Investigator</th>
                        <th>Submitted On</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for review in completed_reviews %}
                    <tr>
                        <td>{{ review.submission.title }}</td>
                        <td>{{ review.submission.primary_investigator.userprofile.full_name }}</td>
                        <td>{{ review.date_submitted|date:"M d, Y" }}</td>
                        <td>
                            <a href="{% url 'review:view_review' review.id %}" class="btn btn-sm btn-info">
                                <i class="fas fa-eye"></i> View
                            </a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script src="https://cdn.datatables.net/buttons/2.2.3/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.2.3/js/buttons.bootstrap4.min.js"></script>
<script>
$(document).ready(function() {
    // Initialize DataTable
    var table = $('#pendingReviewsTable').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: window.location.href,
            type: 'GET',
            data: function(d) {
                d.status = $('#status').val();
                d.study_type = $('#study_type').val();
                d.date_from = $('#date_from').val();
                d.date_to = $('#date_to').val();
            },
            error: function (xhr, error, thrown) {
                console.error('DataTables error:', error);
                console.error('Details:', thrown);
                console.error('Response:', xhr.responseText);
            }
        },
        columns: [
            { data: 'title' },
            { data: 'investigator' },
            { data: 'study_type' },
            { 
                data: 'deadline',
                render: function(data) {
                    return moment(data).format('MMM D, YYYY');
                }
            },
            { 
                data: 'status',
                render: function(data) {
                    return '<span class="status-badge status-' + data.toLowerCase() + '">' + data + '</span>';
                }
            },
            { 
                data: 'days_remaining',
                render: function(data) {
                    let className = data <= 7 ? 'days-danger' : 
                                  data <= 14 ? 'days-warning' : 'days-safe';
                    return '<span class="days-remaining ' + className + '">' + 
                           data + ' days</span>';
                }
            },
            { 
                data: 'actions',
                orderable: false,
                searchable: false
            }
        ],
        order: [[3, 'asc']],
        pageLength: 10,
        dom: 'Bfrtip',
        buttons: [
            'copy', 'excel', 'csv'
        ]
    });

    // Initialize completed reviews table
    $('#completedReviewsTable').DataTable({
        pageLength: 10,
        order: [[2, 'desc']]
    });

    // Filter handling
    $('#applyFilters').click(function() {
        table.ajax.reload();
    });

    $('#resetFilters').click(function() {
        $('#filterForm')[0].reset();
        table.ajax.reload();
    });

    // PDF Export
    $('#exportPDF').click(function() {
        let params = new URLSearchParams({
            export: 'pdf',
            status: $('#status').val(),
            study_type: $('#study_type').val(),
            date_from: $('#date_from').val(),
            date_to: $('#date_to').val()
        });
        window.location.href = window.location.href + '?' + params.toString();
    });
});
</script>
{% endblock %}{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Decline Review Request{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header bg-danger text-white">
                    <h2 class="mb-0">Decline Review Request</h2>
                </div>
                <div class="card-body">
                    <!-- Review Details -->
                    <div class="alert alert-info">
                        <h5>Review Details</h5>
                        <p><strong>Submission:</strong> {{ review_request.submission.title }}</p>
                        <p><strong>Requested By:</strong> {{ review_request.requested_by.userprofile.full_name }}</p>
                        <p><strong>Deadline:</strong> {{ review_request.deadline|date:"F d, Y" }}</p>
                        {% if review_request.message %}
                        <p><strong>Original Request Message:</strong></p>
                        <div class="border-left pl-3">{{ review_request.message|linebreaks }}</div>
                        {% endif %}
                    </div>

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <!-- Reason -->
                        <div class="mb-3">
                            <label for="reason" class="form-label required">Reason for Declining</label>
                            <textarea class="form-control" 
                                      id="reason" 
                                      name="reason" 
                                      rows="4"
                                      required
                                      placeholder="Please provide a detailed reason for declining this review request..."></textarea>
                            <div class="form-text">This message will be sent to the requester and the primary investigator.</div>
                        </div>

                        <!-- Confirmation Checkbox -->
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="confirm" 
                                       required>
                                <label class="form-check-label" for="confirm">
                                    I confirm that I want to decline this review request
                                </label>
                            </div>
                        </div>

                        <!-- Submit Buttons -->
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{% url 'review:review_dashboard' %}" 
                               class="btn btn-secondary me-md-2">
                                <i class="fas fa-arrow-left"></i> Cancel
                            </a>
                            <button type="submit" 
                                    class="btn btn-danger" 
                                    id="submitBtn" 
                                    disabled>
                                <i class="fas fa-times"></i> Decline Review
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.querySelector('form');
        const reasonInput = document.getElementById('reason');
        const confirmCheckbox = document.getElementById('confirm');
        const submitBtn = document.getElementById('submitBtn');

        // Enable/disable submit button based on form state
        function updateSubmitButton() {
            submitBtn.disabled = !(
                reasonInput.value.trim().length >= 10 && 
                confirmCheckbox.checked
            );
        }

        reasonInput.addEventListener('input', updateSubmitButton);
        confirmCheckbox.addEventListener('change', updateSubmitButton);

        // Form validation
        form.addEventListener('submit', function(e) {
            if (!reasonInput.value.trim()) {
                e.preventDefault();
                alert('Please provide a reason for declining.');
                reasonInput.focus();
                return false;
            }

            if (!confirmCheckbox.checked) {
                e.preventDefault();
                alert('Please confirm that you want to decline this review.');
                return false;
            }

            if (reasonInput.value.trim().length < 10) {
                e.preventDefault();
                alert('Please provide a more detailed reason (at least 10 characters).');
                reasonInput.focus();
                return false;
            }
        });
    });
</script>
{% endblock %}{# review/templates/review/forward_review.html #}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Forward Review Request{% endblock %}

{% block page_specific_css %}
<style>
    .review-chain {
        position: relative;
        margin-bottom: 2rem;
    }
    .chain-item {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .chain-connector {
        position: absolute;
        left: 15px;
        top: 30px;
        bottom: 0;
        width: 2px;
        background-color: #dee2e6;
    }
    .chain-node {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #007bff;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        position: relative;
        z-index: 1;
    }
    .chain-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        flex-grow: 1;
    }
    .reviewer-select {
        min-height: 200px;
    }
    .selected-reviewers {
        margin-top: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
    }
    .selected-reviewer {
        display: inline-block;
        background-color: #e9ecef;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <!-- Main Forwarding Form -->
            <div class="card">
                <div class="card-header">
                    <h2>Forward Review Request</h2>
                </div>
                <div class="card-body">
                    <!-- Submission Info -->
                    <div class="alert alert-info">
                        <h5>Submission Details</h5>
                        <p><strong>Title:</strong> {{ review_request.submission.title }}</p>
                        <p><strong>Primary Investigator:</strong> 
                           {{ review_request.submission.primary_investigator.userprofile.full_name }}</p>
                        <p><strong>Study Type:</strong> 
                           {{ review_request.submission.study_type.name }}</p>
                        <p><strong>Current Status:</strong> 
                           <span class="badge bg-{{ review_request.submission.status|lower }}">
                               {{ review_request.submission.get_status_display }}
                           </span>
                        </p>
                    </div>

                    <form method="post" class="needs-validation" novalidate>
                        {% csrf_token %}
                        
                        <!-- Reviewer Selection -->
                        <div class="mb-3">
                            <label class="form-label required">Select Reviewers</label>
                            <select name="reviewers" multiple class="form-select reviewer-select" required>
                                {% for reviewer in available_reviewers %}
                                <option value="{{ reviewer.id }}">
                                    {{ reviewer.userprofile.full_name }} 
                                    ({{ reviewer.groups.first.name }})
                                </option>
                                {% endfor %}
                            </select>
                            <div class="form-text">
                                Hold Ctrl/Cmd to select multiple reviewers
                            </div>
                        </div>

                        <!-- Selected Reviewers Preview -->
                        <div class="selected-reviewers d-none">
                            <h6>Selected Reviewers:</h6>
                            <div id="selectedReviewersList"></div>
                        </div>

                        <!-- Deadline -->
                        <div class="mb-3">
                            <label for="deadline" class="form-label required">Review Deadline</label>
                            <input type="date" 
                                   class="form-control" 
                                   id="deadline" 
                                   name="deadline"
                                   min="{{ min_date }}"
                                   value="{{ suggested_date }}"
                                   required>
                        </div>

                        <!-- Message -->
                        <div class="mb-3">
                            <label for="message" class="form-label required">Message to Reviewers</label>
                            <textarea class="form-control" 
                                      id="message" 
                                      name="message" 
                                      rows="4"
                                      required></textarea>
                        </div>

                        <!-- Forward Permission -->
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="allow_forwarding" 
                                       name="allow_forwarding" 
                                       value="true">
                                <label class="form-check-label" for="allow_forwarding">
                                    Allow these reviewers to forward to others
                                </label>
                            </div>
                        </div>

                        <!-- Submit Buttons -->
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <button type="button" 
                                    class="btn btn-secondary me-md-2" 
                                    onclick="history.back()">
                                Cancel
                            </button>
                            <button type="submit" class="btn btn-primary">
                                Forward Review Request
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <!-- Review Chain Visualization -->
            <div class="card">
                <div class="card-header">
                    <h5 class="card-t{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Request Review Extension{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Request Review Extension</h2>
                </div>
                <div class="card-body">
                    <!-- Review Details -->
                    <div class="alert alert-info">
                        <h5>Review Details</h5>
                        <p><strong>Submission:</strong> {{ review_request.submission.title }}</p>
                        <p><strong>Current Deadline:</strong> {{ review_request.deadline|date:"F d, Y" }}</p>
                        <p><strong>Days Remaining:</strong> {{ review_request.days_until_deadline }}</p>
                    </div>

                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <!-- New Deadline -->
                        <div class="mb-3">
                            <label for="new_deadline" class="form-label">New Deadline</label>
                            <input type="date" 
                                   class="form-control" 
                                   id="new_deadline" 
                                   name="new_deadline"
                                   min="{{ min_date }}"
                                   max="{{ max_date }}"
                                   required>
                            <div class="form-text">Select a new deadline (maximum 30 days extension)</div>
                        </div>

                        <!-- Reason -->
                        <div class="mb-3">
                            <label for="reason" class="form-label">Reason for Extension</label>
                            <textarea class="form-control" 
                                      id="reason" 
                                      name="reason" 
                                      rows="4"
                                      required></textarea>
                            <div class="form-text">Please provide a detailed reason for requesting an extension</div>
                        </div>

                        <!-- Submit Buttons -->
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{% url 'review:review_dashboard' %}" 
                               class="btn btn-secondary me-md-2">
                                <i class="fas fa-times"></i> Cancel
                            </a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-clock"></i> Request Extension
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Validate form before submission
        document.querySelector('form').addEventListener('submit', function(e) {
            var newDeadline = document.getElementById('new_deadline').value;
            var reason = document.getElementById('reason').value;
            
            if (!newDeadline || !reason) {
                e.preventDefault();
                alert('Please fill in all required fields');
                return false;
            }
            
            var selectedDate = new Date(newDeadline);
            var currentDate = new Date();
            
            if (selectedDate <= currentDate) {
                e.preventDefault();
                alert('New deadline must be in the future');
                return false;
            }
        });
    });
</script>
{% endblock %}{# review/templates/review/review_summary.html #}
{% extends 'users/base.html' %}
{% load static %}

{% block title %}Review Summary - {{ submission.title }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="card">
        <div class="card-header">
            <h2>Review Summary</h2>
            <h4>{{ submission.title }}</h4>
        </div>
        <div class="card-body">
            <!-- Submission Details -->
            <div class="alert alert-info">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Primary Investigator:</strong> 
                           {{ submission.primary_investigator.userprofile.full_name }}</p>
                        <p><strong>Study Type:</strong> 
                           {{ submission.study_type.name }}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Version:</strong> {{ submission.version }}</p>
                        <p><strong>Status:</strong> 
                           <span class="badge bg-{{ submission.status|lower }}">
                               {{ submission.get_status_display }}
                           </span>
                        </p>
                    </div>
                </div>
            </div>

            <!-- Reviews List -->
            {% for review in reviews %}
            <div class="card mb-3">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Review by {{ review.reviewer.userprofile.full_name }}</h5>
                        <span class="text-muted">
                            Submitted {{ review.date_submitted|date:"F d, Y H:i" }}
                        </span>
                    </div>
                </div>
                <div class="card-body">
                    {% for response in review.formresponse_set.all %}
                    <div class="mb-4">
                        <h6>{{ response.form.name }}</h6>
                        {% for field, value in response.response_data.items %}
                        <div class="mb-2">
                            <strong>{{ field }}:</strong>
                            <div class="ml-3">{{ value }}</div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endfor %}

                    {% if review.comments %}
                    <div class="mt-3">
                        <h6>Additional Comments</h6>
                        <div class="border-left pl-3">
                            {{ review.comments|linebreaks }}
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% empty %}
            <div class="alert alert-warning">
                No reviews submitted yet.
            </div>
            {% endfor %}

            <!-- IRB Coordinator Actions -->
            {% if can_make_decision and submission.status == 'reviews_completed' %}
            <div class="card mt-4">
                <div class="card-header">
                    <h5 class="mb-0">Make IRB Decision</h5>
                </div>
                <div class="card-body">
                    <form method="post" action="{% url 'review:process_decision' submission.id %}">
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label class="form-label">Decision</label>
                            <select name="decision" class="form-select" required>
                                <option value="">Select decision...</option>
                                <option value="approved">Approve</option>
                                <option value="revision_required">Request Revision</option>
                                <option value="rejected">Reject</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Comments</label>
                            <textarea name="comments" class="form-control" rows="4" required></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary">
                            Submit Decision
                        </button>
                    </form>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{# review/templates/review/process_decision.html #}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Process IRB Decision{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h2>Process IRB Decision</h2>
                    <h5>{{ submission.title }}</h5>
                </div>
                <div class="card-body">
                    <form method="post" class="needs-validation" novalidate>
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label class="form-label required">Decision</label>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="decision" 
                                       value="approved" id="decision_approved" required>
                                <label class="form-check-label" for="decision_approved">
                                    Approve
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="decision"
                                       value="revision_required" id="decision_revision" required>
                                <label class="form-check-label" for="decision_revision">
                                    Request Revision
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="decision"
                                       value="rejected" id="decision_rejected" required>
                                <label class="form-check-label" for="decision_rejected">
                                    Reject
                                </label>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="comments" class="form-label required">Comments</label>
                            <textarea class="form-control" id="comments" name="comments"
                                    rows="5" required></textarea>
                            <div class="invalid-feedback">
                                Please provide comments explaining your decision.
                            </div>
                        </div>

                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{% url 'review:review_summary' submission.id %}" 
                               class="btn btn-secondary me-md-2">Cancel</a>
                            <button type="submit" class="btn btn-primary">Submit Decision</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_specific_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Form validation
        const form = document.querySelector('form');
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Dynamic requirements based on decision
        const decisionInputs = document.querySelectorAll('input[name="decision"]');
        const commentsField = document.getElementById('comments');
        
        decisionInputs.forEach(input => {
            input.addEventListener('change', function() {
                if (this.value === 'revision_required' || this.value === 'rejected') {
                    commentsField.setAttribute('required', '');
                } else {
                    commentsField.removeAttribute('required');
                }
            });
        });
    });
</script>
{% endblock %}<!-- submission/templates/submission_detail.html -->
{% extends 'base.html' %}
{% block content %}
<h2>{{ submission.title }}</h2>
<p>Current Version: {{ submission.version }}</p>
<h3>All Versions</h3>
<ul>
    {% for version in versions %}
        <li>
            Version {{ version.version }} - {{ version.status }} on {{ version.date }}
            <a href="{% url 'submission:view_version' submission.id version.version %}">View</a>
            {% if not forloop.last %}
                <a href="{% url 'submission:compare_versions' submission.id version.version submission.version %}">Compare with Latest</a>
            {% endif %}
        </li>
    {% endfor %}
</ul>
{% endblock %}
<!-- review/templates/review/submit_review.html -->
{% extends 'base.html' %}
{% block content %}
<h2>Submit Review for "{{ submission.title }}" (Version {{ submission.version }})</h2>

{% if review_request.conflict_of_interest_declared is None %}
    <form method="post">
        {% csrf_token %}
        {{ conflict_form.as_p }}
        <button type="submit" class="btn btn-primary">Proceed</button>
    </form>
{% else %}
    <!-- Display Submission Details -->
    <h3>Submission Details</h3>
    <!-- Include any relevant submission information here -->

    <!-- Render Dynamic Forms -->
    <form method="post">
        {% csrf_token %}
        {% for form, form_instance in forms %}
            <h3>{{ form.title }}</h3>
            {{ form_instance.as_p }}
        {% endfor %}
        <label for="comments">Additional Comments:</label>
        <textarea name="comments" id="comments" rows="4"></textarea>
        <button type="submit" class="btn btn-success">Submit Review</button>
    </form>
{% endif %}
{% endblock %}
{% extends 'users/base.html' %}
{% load crispy_forms_tags %}

{% block title %}Review Details{% endblock %}

{% block page_specific_css %}
<style>
    .status-badge {
        padding: 0.4em 0.8em;
        border-radius: 0.25rem;
        font-size: 0.875em;
    }
    .form-response {
        margin-bottom: 2rem;
        padding: 1rem;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
    }
    .form-response h3 {
        color: #2c3e50;
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }
    .response-field {
        margin-bottom: 1rem;
    }
    .response-field label {
        font-weight: bold;
        color: #495057;
    }
    .response-field .value {
        margin-left: 1rem;
    }
    .metadata {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .metadata-item {
        margin-bottom: 0.5rem;
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <!-- Review Header -->
    <div class="card mb-4">
        <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
                <h2 class="mb-0">Review Details</h2>
                <div>
                    {% if can_edit %}
                    <a href="{% url 'review:submit_review' review.id %}" class="btn btn-primary">
                        <i class="fas fa-edit"></i> Edit Review
                    </a>
                    {% endif %}
                    <a href="{% url 'review:review_dashboard' %}" class="btn btn-secondary">
                        <i class="fas fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </div>
        <div class="card-body">
            <!-- Metadata Section -->
            <div class="metadata">
                <div class="row">
                    <div class="col-md-6">
                        <div class="metadata-item">
                            <strong>Submission:</strong> {{ submission.title }}
                        </div>
                        <div class="metadata-item">
                            <strong>Version:</strong> {{ review.submission_version }}
                        </div>
                        <div class="metadata-item">
                            <strong>Reviewer:</strong> {{ review.reviewer.userprofile.full_name }}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="metadata-item">
                            <strong>Submitted:</strong> {{ review.date_submitted|date:"F d, Y H:i" }}
                        </div>
                        <div class="metadata-item">
                            <strong>Status:</strong> 
                            <span class="status-badge status-{{ review_request.status }}">
                                {{ review_request.get_status_display }}
                            </span>
                        </div>
                        <div class="metadata-item">
                            <strong>Requested By:</strong> {{ review_request.requested_by.userprofile.full_name }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Form Responses -->
            {% if form_responses %}
                {% for response in form_responses %}
                <div class="form-response">
                    <h3>{{ response.form.name }}</h3>
                    {% for field_name, field_value in response.response_data.items %}
                    <div class="response-field">
                        <label>{{ field_name }}:</label>
                        <div class="value">
                            {% if field_value|length > 100 %}
                                <pre class="pre-scrollable">{{ field_value }}</pre>
                            {% else %}
                                {{ field_value }}
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            {% else %}
                <div class="alert alert-info">
                    No form responses found for this review.
                </div>
            {% endif %}

            <!-- Comments Section -->
            {% if review.comments %}
            <div class="card mt-4">
                <div class="card-header">
                    <h3 class="mb-0">Additional Comments</h3>
                </div>
                <div class="card-body">
                    {{ review.comments|linebreaks }}
                </div>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Action Buttons -->
    <div class="card">
        <div class="card-body">
            <div class="d-flex justify-content-between">
                <div>
                    {% if is_requester or is_pi %}
                    <a href="{% url 'messaging:compose_message' %}?related_review={{ review.id }}" 
                       class="btn btn-info">
                        <i class="fas fa-envelope"></i> Contact Reviewer
                    </a>
                    {% endif %}
                </div>
                <div>
                    {% if is_pi or is_requester %}
                    <a href="{% url 'submission:download_submission_pdf' submission.id review.submission_version %}" 
                       class="btn btn-secondary">
                        <i class="fas fa-file-pdf"></i> Download Submission Version
                    </a>
                    {% endif %}
                    <button onclick="window.print()" class="btn btn-primary">
                        <i class="fas fa-print"></i> Print Review
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}