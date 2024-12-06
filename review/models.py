from django.db import models
from django.contrib.auth.models import User
from submission.models import Submission
from forms_builder.models import DynamicForm
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
from django.apps import apps
from iRN.constants import get_status_choices

######################
# Status Choice
######################

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

######################
# Review Request
######################

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

    @classmethod
    def can_create_review_request(cls, user):
        """Check if the user can create a review request."""
        # Check if the user is in any of the required groups
        return user.groups.filter(name__in=['IRB', 'OSAR', 'RC']).exists()

    @property
    def is_overdue(self):
        return self.deadline < timezone.now().date()

    @property
    def days_until_deadline(self):
        return (self.deadline - timezone.now().date()).days

    @property
    def has_forwarded_requests(self):
        """Check if this review request has any child requests (has been forwarded)"""
        return self.child_requests.exists()

    @property
    def forward_count(self):
        """Return the number of times this request has been forwarded"""
        return self.child_requests.count()

    def save(self, *args, **kwargs):
        # Ensure submission_version is an integer
        if isinstance(self.submission_version, datetime):
            self.submission_version = self.submission.version
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review Request for {self.submission} (Version {self.submission_version})"

######################
# Review
######################

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    review_request = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    submission_version = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("view_any_review", "Can view any review regardless of assignment"),
            ("change_submission_status", "Can change submission status"),
        ]

    def __str__(self):
        return f"Review by {self.reviewer} for {self.submission}"

######################
# Form Response
######################

class FormResponse(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    form = models.ForeignKey('forms_builder.DynamicForm', on_delete=models.CASCADE)
    response_data = models.JSONField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.form} for {self.review}"

######################
# Notepad
######################
# models.py

class NotepadEntry(models.Model):
    NOTEPAD_TYPES = [
        ('OSAR', 'OSAR'),
        ('IRB', 'IRB'),
        ('RC', 'RC'),
    ]
    
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='notepad_entries')
    notepad_type = models.CharField(max_length=10, choices=NOTEPAD_TYPES)
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_notes', blank=True)

    class Meta:
        verbose_name = 'Notepad Entry'
        verbose_name_plural = 'Notepad Entries'
        ordering = ['-created_at']
        db_table = 'review_notepad_entry'


######################
# Submission Decision
######################

class SubmissionDecision(models.Model):
    DECISION_CHOICES = [
        ('revision_requested', 'Revision Requested'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('provisional_approval', 'Provisional Approval'),
        ('suspended', 'Suspended'),
    ]

    submission = models.ForeignKey('submission.Submission', on_delete=models.CASCADE, related_name='decisions')
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    comments = models.TextField(blank=True)
    decided_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        db_table = 'review_submission_decision'

    def __str__(self):
        return f"{self.get_decision_display()} for {self.submission}"

