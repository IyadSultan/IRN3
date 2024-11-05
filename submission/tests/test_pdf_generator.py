from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from io import BytesIO
import json
from datetime import datetime, timedelta

from submission.models import Submission, FormDataEntry, DynamicForm, StudyType, CoInvestigator
from users.models import Role  # Add this import
from submission.utils.pdf_generator import PDFGenerator, generate_submission_pdf

User = get_user_model()

class TestPDFGenerator(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.pi_user = User.objects.create_user(
            username='pi_user',
            email='pi@example.com',
            password='testpass123',
            first_name='Primary',
            last_name='Investigator'
        )

        # Create co-investigator user
        self.co_investigator = User.objects.create_user(
            username='co_investigator',
            email='co@example.com',
            password='testpass123',
            first_name='Co',
            last_name='Investigator'
        )

        # Create test roles
        self.role1 = Role.objects.create(
            name='Principal Investigator',
            description='Lead researcher'
        )
        self.role2 = Role.objects.create(
            name='Data Analyst',
            description='Analyzes research data'
        )

        # Create study type first
        self.study_type = StudyType.objects.create(
            name='Retrospective'
        )

        # Create a test submission with numeric temporary_id
        self.submission = Submission.objects.create(
            temporary_id=12345,
            title='Test Submission',
            study_type=self.study_type,
            irb_number='IRB123',
            status='draft',
            primary_investigator=self.pi_user,
            date_created=timezone.now(),
            date_submitted=timezone.now()
        )

        # Add co-investigator to submission with multiple roles
        self.co_investigator_relation = CoInvestigator.objects.create(
            submission=self.submission,
            user=self.co_investigator,
            can_edit=True,
            can_submit=True,
            can_view_communications=True
        )
        # Add roles to the co-investigator
        self.co_investigator_relation.roles.add(self.role1, self.role2)

        # Create test dynamic form
        self.dynamic_form = DynamicForm.objects.create(
            name='Test Form'
        )

        # Create test form data entry
        self.form_entry = FormDataEntry.objects.create(
            submission=self.submission,
            form=self.dynamic_form,
            field_name='test_field',
            value='Test Value',
            version=1
        )

    def test_initialization(self):
        """Test PDF generator initialization"""
        buffer = BytesIO()
        pdf_gen = PDFGenerator(buffer, self.submission, 1, self.user)
        
        self.assertEqual(pdf_gen.submission, self.submission)
        self.assertEqual(pdf_gen.version, 1)
        self.assertEqual(pdf_gen.user, self.user)

    def test_version_validation(self):
        """Test that PDFGenerator requires a version"""
        buffer = BytesIO()
        with self.assertRaises(ValueError):
            PDFGenerator(buffer, self.submission, None, self.user)

    def test_field_value_formatting(self):
        """Test field value formatting"""
        buffer = BytesIO()
        pdf_gen = PDFGenerator(buffer, self.submission, 1, self.user)
        
        # Test various input types
        self.assertEqual(pdf_gen.format_field_value(None), "Not provided")
        self.assertEqual(pdf_gen.format_field_value(""), "Not provided")
        self.assertEqual(pdf_gen.format_field_value("test"), "test")
        
        # Test JSON array formatting
        json_array = json.dumps(['item1', 'item2'])
        self.assertEqual(pdf_gen.format_field_value(json_array), "item1, item2")

    def test_pdf_generation(self):
        """Test PDF generation function"""
        try:
            # Verify co-investigators are set up correctly
            co_investigators = CoInvestigator.objects.filter(submission=self.submission)
            self.assertTrue(co_investigators.exists(), "No co-investigators found for submission")
            
            # Verify roles are set up correctly
            co_investigator = co_investigators.first()
            self.assertEqual(co_investigator.roles.count(), 2, "Co-investigator should have 2 roles")
            
            # Test with buffer return
            pdf_buffer = generate_submission_pdf(
                self.submission, 
                version=1, 
                user=self.user, 
                as_buffer=True
            )
            self.assertIsInstance(pdf_buffer, BytesIO)
            
            # Additional verification of PDF content could be added here
            
        except Exception as e:
            import traceback
            self.fail(f"PDF generation failed with error: {str(e)}\nTraceback:\n{traceback.format_exc()}")