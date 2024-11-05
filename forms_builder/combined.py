# forms_builder/admin.py

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from .models import StudyType, DynamicForm, FormField
import json
from reversion.admin import VersionAdmin
from reversion.models import Version

@admin.register(StudyType)
class StudyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class DynamicFormAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate the correct admin URL
        example_json_url = reverse('admin:forms_builder_dynamicform_example_json')
        self.fields['json_input'] = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}),
            help_text=f'Enter form data in JSON format. <a href="{example_json_url}" target="_blank">View Example JSON Format</a>.',
            required=False
        )

    class Meta:
        model = DynamicForm
        fields = ('name', 'version', 'requested_per_investigator', 'study_types', 'json_input')

    def clean_json_input(self):
        json_input = self.cleaned_data.get('json_input')
        if json_input:
            try:
                data = json.loads(json_input)
                if 'fields' not in data:
                    raise forms.ValidationError("JSON must contain a 'fields' key.")
                for field in data['fields']:
                    if 'name' not in field or 'field_type' not in field:
                        raise forms.ValidationError("Each field must contain 'name' and 'field_type'.")
                    if 'displayed_name' not in field:
                        field['displayed_name'] = field['name']  # Use name as fallback
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f"Invalid JSON format: {str(e)}")
        # else:
        #     raise forms.ValidationError("This field is required.")
        return json_input

@admin.register(DynamicForm)
class DynamicFormAdmin(VersionAdmin):
    form = DynamicFormAdminForm
    list_display = ('name', 'version', 'date_created')
    readonly_fields = ('form_json', 'date_created')
    search_fields = ('name', 'version')
    list_filter = ('requested_per_investigator', 'study_types')
    change_form_template = 'admin/forms_builder/dynamicform_change_form.html'

    def form_json(self, obj):
        return format_html('<pre>{}</pre>', obj.to_json())

    form_json.short_description = 'Form JSON'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        json_input = form.cleaned_data.get('json_input')
        if json_input:
            data = json.loads(json_input)
            obj.fields.all().delete()
            for field_data in data.get('fields', []):
                field_name = field_data.get('name', '').lower().replace(' ', '_')
                displayed_name = field_data.get('displayed_name', field_data.get('name'))
                field_type = field_data.get('field_type')
                default_value = field_data.get('default_value', '')
                max_length = field_data.get('max_length')
                rows = field_data.get('rows', 3)
                choices = field_data.get('choices', [])
                choices_str = ','.join(choices) if choices else ''
                required = field_data.get('required', False)
                help_text = field_data.get('help_text', '')
                
                FormField.objects.create(
                    form=obj,
                    name=field_name,
                    displayed_name=displayed_name,
                    field_type=field_type,
                    default_value=default_value,
                    max_length=max_length,
                    rows=rows,
                    choices=choices_str,
                    required=required,
                    help_text=help_text
                )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['json_input'].initial = obj.to_json()
        else:
            form.base_fields['json_input'].initial = '''{
  "fields": [
    {
      "name": "field_name",
      "displayed_name": "Field Display Name",
      "field_type": "text",
      "default_value": "",
      "max_length": 255,
      "choices": [],
      "required": false,
      "help_text": "Enter explanation for this field here"
    }
  ]
}'''
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('example_json/', self.admin_site.admin_view(self.example_json_view), name='forms_builder_dynamicform_example_json'),
            path('<int:object_id>/history/<int:version_id>/', self.admin_site.admin_view(self.revision_view), name='forms_builder_dynamicform_revision'),
        ]
        return custom_urls + urls

    def example_json_view(self, request):
        example_json = '''{
  "fields": [
    {
      "name": "research_title",
      "displayed_name": "Research Title",
      "field_type": "text",
      "default_value": "",
      "max_length": 255,
      "choices": [],
      "required": true,
      "help_text": "Enter the full title of the research project"
    },
    {
      "name": "project_description",
      "displayed_name": "Project Description",
      "field_type": "textarea",
      "default_value": "",
      "max_length": 2000,
      "rows": 5,
      "choices": [],
      "required": true,
      "help_text": "Provide a detailed description of the research project"
    }
  ]
}'''
        context = dict(
            self.admin_site.each_context(request),
            title='Example JSON Format',
            example_json=example_json,
        )
        return TemplateResponse(request, 'admin/forms_builder/example_json.html', context)

    def history_view(self, request, object_id, extra_context=None):
        response = super().history_view(request, object_id, extra_context)
        versions = Version.objects.get_for_object(self.get_object(request, object_id))
        # Pass the versions to the context
        response.context_data['versions'] = versions
        return response

    def revision_view(self, request, object_id, version_id):
        obj = get_object_or_404(self.model, pk=object_id)
        version = get_object_or_404(Version, pk=version_id)
        revision = version._object_version.object  # Get the historical object
        json_input = revision.to_json()  # Get the JSON representation at this version
        context = dict(
            self.admin_site.each_context(request),
            title='Historical Form Version',
            form_name=revision.name,
            version=version,
            json_input=json_input,
        )
        return TemplateResponse(request, 'admin/forms_builder/revision_view.html', context)
from django.apps import AppConfig


class FormsBuilderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "forms_builder"
import os

# try to remove combined.py if it exists
if os.path.exists('combined.py'):
    os.remove('combined.py')

app_directory = "../forms_builder/"
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/admin/forms_builder'

# List all HTML files in the directory
html_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

# Open the output file in append mode to avoid overwriting existing content
with open(output_file, 'a') as outfile:
    for fname in html_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)from django.db import models
import json

# Constants
FIELD_TYPES = [
    ('text', 'Text'),
    ('email', 'Email'),
    ('tel', 'Telephone'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('textarea', 'Text Area'),
    ('checkbox', 'Checkboxes'),
    ('radio', 'Radio Buttons'),
    ('select', 'Dropdown List'),
    ('choice', 'Multiple Choice'),
    ('table', 'Table'),
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
    json_input = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text='Defines the sequence in which forms appear'
    )

    def to_json(self):
        form_dict = {
            'fields': []
        }
        for field in self.fields.all():
            field_dict = {
                'name': field.name,
                'displayed_name': field.displayed_name,
                'field_type': field.field_type,
                'default_value': field.default_value,
                'max_length': field.max_length,
                'rows': field.rows,
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
        ordering = ['order']  # Added this line to set default ordering

class FormField(models.Model):
    form = models.ForeignKey(DynamicForm, related_name='fields', on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
        help_text='Database field name (lowercase with underscores)'
    )
    displayed_name = models.CharField(
        max_length=255,
        help_text='Human-readable field name',
        default='',
    )
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    max_length = models.PositiveIntegerField(blank=True, null=True)
    rows = models.PositiveIntegerField(
        default=3,
        help_text='Number of rows for textarea fields'
    )
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
        return f"{self.displayed_name}{required_mark} ({self.get_field_type_display()})"

    class Meta:
        verbose_name = 'Form Field'
        verbose_name_plural = 'Form Fields'
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
from django.shortcuts import render

# Create your views here.
{% extends "admin/change_form.html" %}
{% load static %}

{% block extrahead %}
{{ block.super }}
<style>
    .submit-row {
        display: flex;
        justify-content: space-between;
    }
</style>
{% endblock %}

{% block after_field_sets %}
{% if form.instance.pk %}
    <h2>Form JSON Representation</h2>
    {{ adminform.instance.form_json|safe }}
{% endif %}
{% endblock %}
{% extends "admin/object_history.html" %}
{% load admin_urls %}
{% block content %}
<h1>Change history: {{ title }}</h1>
<table class="history">
    <thead>
        <tr>
            <th>Action time</th>
            <th>Action</th>
            <th>User</th>
            <th>Change message</th>
            <th>Version</th>
        </tr>
    </thead>
    <tbody>
        {% for entry in action_list %}
        <tr class="{% cycle 'row1' 'row2' %}">
            <td>{{ entry.action_time }}</td>
            <td>{{ entry.get_action_flag_display }}</td>
            <td>{{ entry.user }}</td>
            <td>{{ entry.get_change_message }}</td>
            <td>
                {% if entry.get_action_flag_display == 'Changed' %}
                    {% with version=versions|get_by_field:"revision_id, entry.revision_id" %}
                        {% if version %}
                            <a href="{% url 'admin:forms_builder_dynamicform_revision' object_id=object.pk version_id=version.id %}">View Version</a>
                        {% endif %}
                    {% endwith %}
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
{% extends "admin/base_site.html" %}
{% load static %}

{% block content %}
<h1>{{ title }}</h1>
<div class="help">
    <h2>JSON Format Guide</h2>
    <p>Instructions for converting forms to JSON format:</p>
    <ul>
        <li><strong>Field Names:</strong>
            <ul>
                <li>Use lowercase with underscores (snake_case)</li>
                <li>Be descriptive but concise</li>
                <li>Avoid spaces and special characters</li>
                <li>Example: "principal_investigator_name" not "PI Name"</li>
            </ul>
        </li>
        <li><strong>Field Types Available:</strong>
            <ul>
                <li><code>text</code>: Single line text input</li>
                <li><code>textarea</code>: Multi-line text input (specify rows)</li>
                <li><code>email</code>: Email validation</li>
                <li><code>tel</code>: Telephone number</li>
                <li><code>number</code>: Numeric input</li>
                <li><code>date</code>: Date picker</li>
                <li><code>checkbox</code>: Multiple selections</li>
                <li><code>radio</code>: Single selection</li>
                <li><code>select</code>: Dropdown list</li>
                <li><code>table</code>: Tabular data input</li>
            </ul>
        </li>
        <li><strong>Required Properties:</strong>
            <ul>
                <li><code>name</code>: Field identifier (snake_case)</li>
                <li><code>field_type</code>: One of the types above</li>
                <li><code>default_value</code>: Initial value (can be empty)</li>
                <li><code>max_length</code>: For text/textarea (null for others)</li>
                <li><code>rows</code>: For textarea fields (default: 3)</li>
                <li><code>choices</code>: Array for checkbox/radio/select</li>
                <li><code>required</code>: true/false</li>
                <li><code>help_text</code>: Field description/instructions</li>
            </ul>
        </li>
    </ul>
</div>

<h3>Example JSON Format:</h3>
<pre>{{ example_json }}</pre>

<p><a href="javascript:history.back();" class="button">Back to Form</a></p>

<style>
    .help {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .help ul {
        margin-left: 20px;
    }
    .help ul ul {
        margin-top: 5px;
        margin-bottom: 15px;
    }
    code {
        background: #e9ecef;
        padding: 2px 6px;
        border-radius: 3px;
    }
</style>
{% endblock %}
{% extends "admin/object_history.html" %}
{% load i18n admin_urls %}

{% block content %}
<div id="content-main">
    <h1>History for {{ object|truncatewords:"18" }}</h1>
    
    {% if version_list %}
    <div class="module">
        {% for version in version_list %}
        <div class="version-entry" style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <h3>Revision from {{ version.date_created }}</h3>
            <p>
                <strong>User:</strong> {{ version.user }}<br>
                <strong>Comment:</strong> {{ version.comment }}
            </p>
            <div class="json-view" style="background: #f5f5f5; padding: 10px; white-space: pre-wrap;">
                <code>{{ version.json_data }}</code>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <p>{% trans "This object doesn't have a change history." %}</p>
    {% endif %}
</div>
{% endblock %}
{% extends "admin/base_site.html" %}
{% load static %}
{% block content %}
<h1>{{ title }}</h1>
<p><strong>Form Name:</strong> {{ form_name }}</p>
<p><strong>Version ID:</strong> {{ version.pk }}</p>
<h2>Form JSON at This Version</h2>
<pre>{{ json_input }}</pre>
<p><a href="{% url 'admin:forms_builder_dynamicform_changelist' %}">Back to Forms</a></p>
{% endblock %}
