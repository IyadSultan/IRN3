from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
from django.db.models.signals import post_save
from django.test.utils import override_settings
from ..models import Review, ReviewRequest, Submission
from ..utils.pdf_generator import generate_review_dashboard_pdf
from submission.models import StudyType
from users.models import UserProfile
from users.signals import create_user_profile  # Import the signal handler

class PDFGeneratorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Disconnect the signal temporarily
        post_save.disconnect(create_user_profile, sender=User)

        try:
            # Create test users without triggering signals
            cls.user = User.objects.create(
                username='testuser',
                email='test@example.com',
            )
            cls.pi_user = User.objects.create(
                username='pi_user',
                email='pi@example.com',
            )
            
            # Create user profiles manually
            UserProfile.objects.create(
                user=cls.user,
                full_name="Test User"
            )
            UserProfile.objects.create(
                user=cls.pi_user,
                full_name="PI User"
            )

            # Create study type
            cls.study_type = StudyType.objects.create(
                name="Test Study",
                description="Test Study Description"
            )

            # Create test submission
            cls.submission = Submission.objects.create(
                title="Test Submission",
                primary_investigator=cls.pi_user,
                study_type=cls.study_type,
                version=1
            )

        finally:
            # Reconnect the signal
            post_save.connect(create_user_profile, sender=User)

    def setUp(self):
        # Create review requests
        self.pending_review = ReviewRequest.objects.create(
            submission=self.submission,
            submission_version=1,
            requested_by=self.pi_user,
            requested_to=self.user,
            deadline=timezone.now().date() + timedelta(days=7),
            status='pending'
        )

        self.completed_review = ReviewRequest.objects.create(
            submission=self.submission,
            submission_version=1,
            requested_by=self.pi_user,
            requested_to=self.user,
            deadline=timezone.now().date() - timedelta(days=7),
            status='completed'
        )

        # Create completed review
        self.review = Review.objects.create(
            review_request=self.completed_review,
            reviewer=self.user,
            submission=self.submission,
            submission_version=1,
            date_submitted=timezone.now()
        )

    def test_generate_pdf_as_buffer(self):
        """Test PDF generation returns a BytesIO buffer"""
        pending_reviews = ReviewRequest.objects.filter(status='pending')
        completed_reviews = Review.objects.all()
        
        pdf_buffer = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=True
        )
        
        self.assertIsInstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generate_pdf_as_response(self):
        """Test PDF generation returns an HTTP response"""
        pending_reviews = ReviewRequest.objects.filter(status='pending')
        completed_reviews = Review.objects.all()
        
        response = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=False
        )
        
        # Check response properties
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="review_dashboard.pdf"'
        )
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_content_structure(self):
        """Test the structure of generated PDF content"""
        pending_reviews = ReviewRequest.objects.filter(status='pending')
        completed_reviews = Review.objects.all()
        
        pdf_buffer = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=True
        )
        
        # Convert PDF to text for content checking
        pdf_content = pdf_buffer.getvalue()
        
        # Basic size check
        self.assertGreater(len(pdf_content), 100)  # PDF should have reasonable size

    def test_empty_reviews(self):
        """Test PDF generation with empty review sets"""
        pending_reviews = ReviewRequest.objects.none()
        completed_reviews = Review.objects.none()
        
        pdf_buffer = generate_review_dashboard_pdf(
            pending_reviews,
            completed_reviews,
            self.user,
            as_buffer=True
        )
        
        # Check if PDF is still generated
        self.assertIsInstance(pdf_buffer, BytesIO)
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF')) 