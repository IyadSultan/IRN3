# submission/tests/test_models.py

from django.test import TestCase
from django.contrib.auth.models import User
from submission.models import (
    Submission,
    CoInvestigator,
    ResearchAssistant,
    FormDataEntry,
    Document,
    VersionHistory,
    SystemSettings,
    StatusChoice,
)
from forms_builder.models import StudyType, DynamicForm
from users.models import Role
from django.utils import timezone


class SubmissionModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.study_type = StudyType.objects.create(name='Retrospective')
        self.submission = Submission.objects.create(
            title='Test Submission',
            study_type=self.study_type,
            primary_investigator=self.user,
            status='draft',
            date_created=timezone.now(),
        )
        self.role = Role.objects.create(name='Data Analyst')
        self.coinvestigator_user = User.objects.create_user(username='coinvestigator')
        self.coinvestigator = CoInvestigator.objects.create(
            submission=self.submission,
            user=self.coinvestigator_user,
            can_edit=True,
        )
        self.coinvestigator.roles.add(self.role)

    def test_submission_str(self):
        self.assertEqual(
            str(self.submission),
            f"{self.submission.title} (ID: {self.submission.temporary_id}, Version: {self.submission.version})",
        )

    def test_coinvestigator_str(self):
        self.assertEqual(
            str(self.coinvestigator),
            f"{self.coinvestigator_user.get_full_name()} - {self.submission.temporary_id}",
        )

    def test_increment_version(self):
        old_version = self.submission.version
        self.submission.increment_version()
        self.assertEqual(self.submission.version, old_version + 1)
        self.assertTrue(
            VersionHistory.objects.filter(
                submission=self.submission, version=self.submission.version
            ).exists()
        )

    def test_system_settings_email(self):
        SystemSettings.objects.create(system_email='system@example.com')
        self.assertEqual(SystemSettings.get_system_email(), 'system@example.com')

    def test_status_choice_caching(self):
        StatusChoice.objects.create(code='approved', label='Approved')
        choices = get_status_choices()
        self.assertIn(('approved', 'Approved'), choices)
