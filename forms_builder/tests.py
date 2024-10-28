# forms_builder/tests.py

from django.test import TestCase
from .models import StudyType, DynamicForm, FormField

class FormsBuilderTestCase(TestCase):
    def setUp(self):
        # Create study types
        self.study_type1 = StudyType.objects.create(name='Retrospective Chart Review')
        self.study_type2 = StudyType.objects.create(name='Prospective')
        # Create a form
        self.form = DynamicForm.objects.create(
            name='Consent Form',
            version='1.0',
            requested_per_investigator=True
        )
        self.form.study_types.add(self.study_type1, self.study_type2)
        # Add fields to the form
        self.field1 = FormField.objects.create(
            form=self.form,
            name='Participant Name',
            field_type='text',
            max_length=100
        )
        self.field2 = FormField.objects.create(
            form=self.form,
            name='Date of Birth',
            field_type='date'
        )
        self.field3 = FormField.objects.create(
            form=self.form,
            name='Gender',
            field_type='choice',
            choices='Male,Female,Other'
        )

    def test_form_creation(self):
        self.assertEqual(self.form.name, 'Consent Form')
        self.assertEqual(self.form.version, '1.0')
        self.assertTrue(self.form.requested_per_investigator)
        self.assertEqual(self.form.fields.count(), 3)

    def test_field_attributes(self):
        self.assertEqual(self.field1.name, 'Participant Name')
        self.assertEqual(self.field1.field_type, 'text')
        self.assertEqual(self.field1.max_length, 100)
        self.assertEqual(self.field2.field_type, 'date')
        self.assertEqual(self.field3.choices, 'Male,Female,Other')

    def test_form_serialization(self):
        json_output = self.form.to_json()
        self.assertIn('"name": "Consent Form"', json_output)
        self.assertIn('"field_type": "text"', json_output)
        self.assertIn('"choices": ["Male", "Female", "Other"]', json_output)
