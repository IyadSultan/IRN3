from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
from submission.models import Submission, VersionHistory
from forms_builder.models import DynamicForm, StudyType
from review.models import ReviewRequest, Review

class ReviewModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        
        # Create IRB Member group
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        
        # Create test study type and submission
        self.study_type = StudyType.objects.create(name='Test Study')
        self.submission = Submission.objects.create(
            title='Test Submission',
            primary_investigator=self.admin_user,
            study_type=self.study_type,
            status='submitted',
            version=1
        )

    def test_review_request_creation(self):
        review_request = ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            deadline=timezone.now().date() + timedelta(days=7),
            status='pending'
        )
        self.assertEqual(review_request.submission_version, 1)
        self.assertEqual(review_request.status, 'pending')

    def test_review_creation(self):
        review_request = ReviewRequest.objects.create(
            submission=self.submission,
            requested_by=self.admin_user,
            requested_to=self.reviewer,
            submission_version=1,
            deadline=timezone.now().date() + timedelta(days=7),
            status='pending'
        )
        
        review = Review.objects.create(
            review_request=review_request,
            reviewer=self.reviewer,
            submission=self.submission,
            submission_version=1,
            comments='Test review comments'
        )
        
        self.assertEqual(review.submission_version, 1)
        self.assertEqual(review.reviewer, self.reviewer)