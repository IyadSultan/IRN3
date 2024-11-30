# iRN (intelligent Research Navigator) Structure Documentation

## Application Tree 
```
📦 IRN3
┣ 📂 iRN (project root)
┃ ┣ 📜 settings.py
┃ ┣ 📜 urls.py
┃ ┗ 📜 wsgi.py
┣ 📂 submission
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
┃ ┃ ┣ 📜 dashboard.html
┃ ┃ ┣ 📜 start_submission.html
┃ ┃ ┣ 📜 dynamic_form.html
┃ ┃ ┣ 📜 submission_review.html
┃ ┃ ┣ 📜 review.html
┃ ┃ ┣ 📜 compare_versions.html
┃ ┃ ┣ 📜 version_history.html
┃ ┃ ┣ 📜 submission_forms.html
┃ ┃ ┣ 📜 edit_submission.html
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┣ 📜 urls.py
┃ ┗ 📜 utils.py
┣ 📂 users
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
┃ ┃ ┣ 📜 base.html
┃ ┃ ┣ 📜 profile.html
┃ ┃ ┣ 📜 dashboard.html
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 messaging
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
┃ ┃ ┣ 📜 inbox.html
┃ ┃ ┣ 📜 sent_messages.html
┃ ┃ ┣ 📜 archived_messages.html
┃ ┃ ┣ 📜 compose_message.html
┃ ┃ ┣ 📜 view_message.html
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 forms_builder
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
┃ ┃ ┣ 📜 admin/forms_builder/example_json.html
┃ ┃ ┣ 📜 admin/forms_builder/revision_view.html
┃ ┃ ┣ 📜 admin/forms_builder/dynamicform_history.html
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 static
┃ ┣ 📂 css
┃ ┣ 📂 js
┃ ┗ 📂 images
┗ 📜 manage.py
```

## Models

### Users App
```python
ROLE_CHOICES = [
    ('KHCC investigator', 'KHCC investigator'),
    ('Non-KHCC investigator', 'Non-KHCC investigator')
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=255, default='King Hussein Cancer Center')
    mobile = models.CharField(max_length=20)
    khcc_employee_number = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    full_name = models.CharField(
        max_length=255,
        default='',
        help_text='Full name (at least three names required)'
    )

class Document(models.Model):
    DOCUMENT_CHOICES = [
        ('GCP', 'Good Clinical Practice Certificate'),
        ('QRC', 'Qualitative Record Certificate'),
        ('CTC', 'Consent Training Certificate'),
        ('CV', 'Curriculum Vitae'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_CHOICES)
    other_document_name = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### Submission App
```python
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('revision_requested', 'Revision Requested'),
    ('under_revision', 'Under Revision'),
    ('accepted', 'Accepted'),
    ('suspended', 'Suspended'),
    ('finished', 'Finished'),
    ('terminated', 'Terminated'),
]

class Submission(models.Model):
    temporary_id = models.AutoField(primary_key=True)
    khcc_number = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=255)
    primary_investigator = models.ForeignKey(
        User, related_name='primary_investigations', on_delete=models.CASCADE
    )
    study_type = models.ForeignKey(StudyType, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    is_locked = models.BooleanField(default=False)

class CoInvestigator(models.Model):
    submission = models.ForeignKey('Submission', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, related_name='coinvestigators')
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['submission', 'user']
        ordering = ['order']

class ResearchAssistant(models.Model):
    submission = models.ForeignKey('Submission', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    can_view_communications = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['submission', 'user']

class FormDataEntry(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='form_data_entries', on_delete=models.CASCADE
    )
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    date_saved = models.DateTimeField(auto_now=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['submission', 'form', 'field_name']),
        ]

class Document(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='documents', on_delete=models.CASCADE
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpeg', 'jpg', 'doc', 'docx', 'txt']

class VersionHistory(models.Model):
    submission = models.ForeignKey(
        Submission, related_name='version_histories', on_delete=models.CASCADE
    )
    version = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateTimeField()
```

### Forms Builder App
```python
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
]

class StudyType(models.Model):
    name = models.CharField(max_length=255, unique=True)

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
```

### Messaging App
```python
class Message(models.Model):
    MESSAGE_TYPES = [
        ('system', 'System Message'),
        ('user', 'User Message'),
        ('notification', 'Notification')
    ]
    
    submission = models.ForeignKey('submission.Submission', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.PROTECT)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.PROTECT)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    date_read = models.DateTimeField(null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    is_read = models.BooleanField(default=False)

class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    file = models.FileField(upload_to='message_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class MessageReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='read_statuses', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

class Comment(models.Model):
    message = models.ForeignKey(Message, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
```

## Views and Functions

### Submission Views
```python
def dashboard(request):
    """Display user's submissions dashboard"""

def start_submission(request, submission_id=None):
    """Start new submission or edit existing one"""

def submission_form(request, submission_id, form_id):
    """Handle dynamic form submission and display"""

def submission_review(request, submission_id):
    """Review submission before final submission"""

def version_history(request, submission_id):
    """View version history of submission"""

def compare_versions(request, submission_id, version1, version2):
    """Compare two versions of a submission"""

def document_delete(request, submission_id, document_id):
    """Delete document from submission"""

def download_submission_pdf(request, submission_id, version=None):
    """Generate and download PDF version of submission"""
```

### Utility Functions
```python
def generate_submission_pdf(submission, version=None, user=None, as_buffer=False):
    """Generate PDF for submission"""

def get_system_user():
    """Get or create system user for automated actions"""

def validate_submission(submission):
    """Validate entire submission"""

def has_edit_permission(user, submission):
    """Check if user has permission to edit submission"""

def get_next_form(submission, current_form):
    """Get next form in sequence"""

def get_previous_form(submission, current_form):
    """Get previous form in sequence"""

def check_researcher_documents(submission):
    """Verify all required documents are uploaded"""
```

## URL Patterns

### Main URLs (iRN/urls.py)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('submission.urls')),
    path('users/', include('users.urls')),
    path('messages/', include('messaging.urls')),
    path('forms/', include('forms_builder.urls')),
]
```

### Submission URLs (submission/urls.py)
```python
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start-submission/', views.start_submission, name='start_submission'),
    path('start-submission/<int:submission_id>/', views.start_submission, name='start_submission_with_id'),
    path('submission-form/<int:submission_id>/<int:form_id>/', views.submission_form, name='submission_form'),
    path('submission-review/<int:submission_id>/', views.submission_review, name='submission_review'),
    path('version-history/<int:submission_id>/', views.version_history, name='version_history'),
    path('compare-versions/<int:submission_id>/<int:version1>/<int:version2>/', views.compare_versions, name='compare_versions'),
    path('document-delete/<int:submission_id>/<int:document_id>/', views.document_delete, name='document_delete'),
]
```

## Dependencies
- Django 5.1.2
- Python 3.10.9
- ReportLab (PDF generation)
- django-crispy-forms
- django-autocomplete-light
- Other requirements in requirements.txt

## Key Features
1. Dynamic Form Building
   - Custom form creation
   - Multiple field types support
   - Conditional validation
   - Form sequencing

2. Submission Management
   - Version control
   - Status tracking
   - PDF generation
   - Document management
   - Multi-step submission process

3. User Management
   - Role-based access control
   - Profile management
   - Department organization
   - Permissions system

4. Messaging System
   - Internal communication
   - File attachments
   - System notifications
   - Message tracking

5. PDF Generation
   - Dynamic content generation
   - Version-specific reports
   - Formatted output
   - Document attachments

## Database Schema
The application uses a relational database with the following key relationships:
- User -> UserProfile (One-to-One)
- Submission -> StudyType (Many-to-One)
- StudyType -> DynamicForm (Many-to-Many through StudyTypeForm)
- DynamicForm -> FormField (Many-to-Many through FormFieldOrder)
- Submission -> FormDataEntry (One-to-Many)
- Message -> MessageAttachment (One-to-Many)
- Submission -> Document (One-to-Many)
```

This structure document now provides a complete overview of the iRN system, including all models, relationships, views, and functionality. Would you like me to expand on any particular section?