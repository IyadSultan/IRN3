# forms_builder/models.py

from django.db import models
import json

# Constants
FIELD_TYPES = [
    ('text', 'Text'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('choice', 'Multiple Choice'),
    ('dropdown', 'Dropdown List'),
    # Add more as needed
]

class StudyType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Study Type'
        verbose_name_plural = 'Study Types'

class DynamicForm(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    requested_per_investigator = models.BooleanField(default=False)
    study_types = models.ManyToManyField(StudyType, related_name='forms')

    def to_json(self):
        form_dict = {
            'fields': []
        }
        for field in self.fields.all():
            field_dict = {
                'name': field.name,
                'field_type': field.field_type,
                'default_value': field.default_value,
                'max_length': field.max_length,
                'choices': field.choices.split(',') if field.choices else [],
                'required': field.required,
                'help_text': field.help_text,
            }
            form_dict['fields'].append(field_dict)
        return json.dumps(form_dict, indent=2)

    def __str__(self):
        return f"{self.name} (v{self.version})"

    class Meta:
        verbose_name = 'Dynamic Form'
        verbose_name_plural = 'Dynamic Forms'

class FormField(models.Model):
    form = models.ForeignKey(DynamicForm, related_name='fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    max_length = models.PositiveIntegerField(blank=True, null=True)
    choices = models.TextField(
        blank=True,
        null=True,
        help_text='Comma-separated values for choices.'
    )
    required = models.BooleanField(
        default=False,
        help_text='Is this field mandatory?'
    )
    help_text = models.TextField(
        blank=True,
        null=True,
        help_text='Explanatory text to be shown with the field.'
    )

    def __str__(self):
        required_mark = '*' if self.required else ''
        return f"{self.name}{required_mark} ({self.get_field_type_display()})"

    class Meta:
        verbose_name = 'Form Field'
        verbose_name_plural = 'Form Fields'
