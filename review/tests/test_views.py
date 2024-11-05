from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from django.utils import timezone
from datetime import timedelta
from submission.models import Submission, VersionHistory
from forms_builder.models import DynamicForm, StudyType
from review.models import ReviewRequest, Review

class ReviewViewTests(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_review_dashboard_view(self):
        self.client.login(username='reviewer', password='password123')
        response = self.client.get(reverse('review:review_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_create_review_request_view(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(
            reverse('review:create_review_request', 
            args=[self.submission.pk])
        )
        self.assertEqual(response.status_code, 200) 