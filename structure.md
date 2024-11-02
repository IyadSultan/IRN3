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
┃ ┃ ┗ 📜 submission_review.html
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┣ 📜 urls.py
┃ ┗ 📜 utils.py
┣ 📂 users
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
┃ ┃ ┣ 📜 base.html
┃ ┃ ┣ 📜 profile.html
┃ ┃ ┗ 📜 dashboard.html
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 messaging
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 forms_builder
┃ ┣ 📂 migrations
┃ ┣ 📂 templates
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
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[
        ('PI', 'Primary Investigator'),
        ('CO_I', 'Co-Investigator'),
        ('RA', 'Research Assistant'),
        ('ADMIN', 'Administrator'),
        ('REVIEWER', 'Reviewer')
    ])
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    institution = models.CharField(max_length=200)
    orcid_id = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Submission App
```python
class Submission(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('revisions_requested', 'Revisions Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    temporary_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500)
    study_type = models.ForeignKey('StudyType', on_delete=models.PROTECT)
    primary_investigator = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    version = models.IntegerField(default=1)
    is_locked = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)

class StudyType(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    forms = models.ManyToManyField('forms_builder.DynamicForm', through='StudyTypeForm')
    required_documents = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StudyTypeForm(models.Model):
    study_type = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    dynamic_form = models.ForeignKey('forms_builder.DynamicForm', on_delete=models.CASCADE)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']

class Document(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    description = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### Forms Builder App
```python
class DynamicForm(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    fields = models.ManyToManyField('FormField', through='FormFieldOrder')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('select', 'Select'),
        ('multiselect', 'Multi Select'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes'),
        ('date', 'Date Input'),
        ('file', 'File Upload')
    ]
    
    name = models.CharField(max_length=200)
    displayed_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    help_text = models.TextField(blank=True)
    choices = models.JSONField(null=True, blank=True)
    validation_rules = models.JSONField(null=True, blank=True)

class FormFieldOrder(models.Model):
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']

class FormDataEntry(models.Model):
    submission = models.ForeignKey('submission.Submission', on_delete=models.CASCADE)
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=200)
    value = models.TextField()
    version = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
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