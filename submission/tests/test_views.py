# submission/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from submission.models import Submission, StudyType
from django.utils import timezone


class SubmissionViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.study_type = StudyType.objects.create(name='Retrospective')
        self.submission = Submission.objects.create(
            title='Test Submission',
            study_type=self.study_type,
            primary_investigator=self.user,
            status='draft',
            date_created=timezone.now(),
        )

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('submission:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Submission')

    def test_start_submission_view_get(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('submission:start_submission'))
        self.assertEqual(response.status_code, 200)

    def test_start_submission_view_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('submission:start_submission'),
            {
                'title': 'New Submission',
                'study_type': self.study_type.id,
                'is_primary_investigator': 'on',
                'action': 'save_continue',
            },
        )
        self.assertEqual(response.status_code, 302)
        new_submission = Submission.objects.get(title='New Submission')
        self.assertEqual(new_submission.primary_investigator, self.user)

    def test_edit_submission_no_permission(self):
        other_user = User.objects.create_user(
            username='otheruser', password='testpass'
        )
        self.client.login(username='otheruser', password='testpass')
        response = self.client.get(
            reverse('submission:edit_submission', args=[self.submission.id])
        )
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'You do not have permission to edit this submission.')
