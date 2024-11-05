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
