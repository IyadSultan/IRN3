from django.test import TestCase
from django.contrib.auth.models import User, Group
from forms_builder.models import DynamicForm
from review.forms import ReviewRequestForm, ConflictOfInterestForm
from django.utils import timezone
from datetime import timedelta

class ReviewFormTests(TestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user('reviewer', 'reviewer@test.com', 'password123')
        self.irb_group = Group.objects.create(name='IRB Member')
        self.reviewer.groups.add(self.irb_group)
        self.test_form = DynamicForm.objects.create(
            name='Test Form',
            description='Test form'
        )

    def test_review_request_form_validation(self):
        form_data = {
            'requested_to': self.reviewer.id,
            'message': 'Please review',
            'deadline': (timezone.now() + timedelta(days=7)).date(),
            'selected_forms': [self.test_form.id],
            'submission_version': 1
        }
        form = ReviewRequestForm(data=form_data)
        self.assertTrue(form.is_valid()) 