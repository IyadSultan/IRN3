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

app_directory = r'C:\Users\isult\Dropbox\AI\Projects\IRN3\review'
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = r'C:\Users\isult\Dropbox\AI\Projects\IRN3\review\templates\review'
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)# review/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import ReviewRequest
from forms_builder.forms.models import Form as DynamicForm

class ReviewRequestForm(forms.ModelForm):
    requested_to = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='IRB Member'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    selected_forms = forms.ModelMultipleChoiceField(
        queryset=DynamicForm.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ReviewRequest
        fields = ['requested_to', 'message', 'deadline', 'selected_forms']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

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
# review/models.py

from django.db import models
from django.contrib.auth.models import User
from submission.models import Submission
from forms_builder.models import DynamicForm
from datetime import datetime

class ReviewRequest(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
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
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
            ('completed', 'Completed')
        ],
        default='pending'
    )
    selected_forms = models.ManyToManyField(DynamicForm)
    conflict_of_interest_declared = models.BooleanField(null=True)
    conflict_of_interest_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    comments = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for {self.submission}"

class FormResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    response_data = models.JSONField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.form} for {self.review}"
from django.test import TestCase, Client
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

app_name = 'review'

urlpatterns = [
    path('', views.review_dashboard, name='review_dashboard'),
    path('dashboard/', views.review_dashboard, name='review_dashboard'),
    path('create/<int:submission_id>/', views.create_review_request, name='create_review_request'),
    path('submit/<int:review_request_id>/', views.submit_review, name='submit_review'),
]
# review/utils.py

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


<!-- review/templates/review/create_review_request.html -->
{% extends 'base.html' %}
{% block content %}
<h2>Create Review Request for "{{ submission.title }}" (Version {{ submission.version }})</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Send Review Request</button>
</form>
{% endblock %}

<!-- review/templates/review/review_dashboard.html -->
{% extends 'base.html' %}
{% block content %}
<h2>Review Dashboard</h2>
<h3>Pending Reviews</h3>
<ul>
    {% for review_request in pending_reviews %}
        <li>
            <a href="{% url 'review:submit_review' review_request.id %}">
                {{ review_request.submission.title }} (Version {{ review_request.submission.version }})
            </a>
            - Deadline: {{ review_request.deadline }}
        </li>
    {% empty %}
        <li>No pending reviews.</li>
    {% endfor %}
</ul>
<h3>Completed Reviews</h3>
<ul>
    {% for review in completed_reviews %}
        <li>
            {{ review.submission.title }} (Version {{ review.submission.version }}) - Submitted on {{ review.date_submitted }}
        </li>
    {% empty %}
        <li>No completed reviews.</li>
    {% endfor %}
</ul>
{% endblock %}
<!-- submission/templates/submission_detail.html -->
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
