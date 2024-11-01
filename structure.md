# iRN (intelligent Research Navigator) Structure Documentation

## Application Tree 


📦 IRN3
┣ 📂 iRN (project root)
┃ ┣ 📜 settings.py
┃ ┣ 📜 urls.py
┃ ┗ 📜 wsgi.py
┣ 📂 submission
┃ ┣ 📂 migrations
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┣ 📜 urls.py
┃ ┗ 📜 utils.py
┣ 📂 users
┃ ┣ 📂 migrations
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 messaging
┃ ┣ 📂 migrations
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 forms_builder
┃ ┣ 📂 migrations
┃ ┣ 📜 models.py
┃ ┣ 📜 views.py
┃ ┗ 📜 urls.py
┣ 📂 templates
┣ 📂 static
┗ 📜 manage.py

## Models

### Users App

python
class UserProfile(models.Model):
user = OneToOneField(User)
role = CharField()
department = CharField()
phone = CharField()
# ... other user-related fields

### Submission App

python
class Submission(models.Model):
    temporary_id = CharField()
    title = CharField()
    study_type = ForeignKey(StudyType)
    primary_investigator = ForeignKey(User)
    status = CharField()
    version = IntegerField()
    date_created = DateTimeField()
    date_submitted = DateTimeField()
    # ... other submission fields

class StudyType(models.Model):
    name = CharField()
    description = TextField()
    forms = ManyToManyField(DynamicForm)
    # ... other study type fields

### Forms Builder App

python
class DynamicForm(models.Model):
    name = CharField()
    description = TextField()
    fields = ManyToManyField(FormField)
    # ... other form fields

class FormField(models.Model):
    name = CharField()
    displayed_name = CharField()
    field_type = CharField()
    required = BooleanField()
    # ... other field properties

class FormDataEntry(models.Model):
    submission = ForeignKey(Submission)
    form = ForeignKey(DynamicForm)
    field_name = CharField()
    value = TextField()
    version = IntegerField()

### Messaging App

python
class Message(models.Model):
    submission = ForeignKey(Submission)
    sender = ForeignKey(User)
    recipient = ForeignKey(User)
    subject = CharField()
    content = TextField()
    date_sent = DateTimeField()
    message_type = CharField()
    # ... other message fields

class MessageAttachment(models.Model):
    message = ForeignKey(Message)
    file = FileField()

## Views Summary

### Submission Views
```python
def submission_list(request)
def submission_create(request)
def submission_detail(request, submission_id)
def submission_review(request, submission_id)
def submission_edit(request, submission_id)
def download_submission_pdf(request, submission_id)
```

### Users Views
```python
def profile_view(request)
def profile_edit(request)
def user_dashboard(request)
```

### Forms Builder Views
```python
def form_builder(request)
def form_preview(request, form_id)
def form_edit(request, form_id)
```

### Messaging Views
```python
def inbox(request)
def message_detail(request, message_id)
def send_message(request)
```

## Key Utilities
```python
def generate_submission_pdf(submission)
def get_system_user()
def validate_submission(submission)
```

## URL Patterns

### Main URLs
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('submission.urls')),
    path('users/', include('users.urls')),
    path('messages/', include('messaging.urls')),
    path('forms/', include('forms_builder.urls')),
]
```

## Key Features
1. Dynamic Form Building
   - Custom form creation
   - Field type support (text, select, checkbox, etc.)
   - Form validation

2. Submission Management
   - Version control
   - Status tracking
   - PDF generation
   - Document attachments

3. User Management
   - Role-based access control
   - Profile management
   - Department organization

4. Messaging System
   - Internal communication
   - File attachments
   - System notifications

5. PDF Generation
   - Submission reports
   - Dynamic form data inclusion
   - Formatted output

## Dependencies
- Django 5.1.2
- Python 3.10.9
- ReportLab (PDF generation)
- Other requirements in requirements.txt

## Database Schema
The application uses a relational database with the following key relationships:
- User -> UserProfile (One-to-One)
- Submission -> StudyType (Many-to-One)
- StudyType -> DynamicForm (Many-to-Many)
- Submission -> FormDataEntry (One-to-Many)
- Message -> MessageAttachment (One-to-Many)

Would you like me to add any additional sections or provide more detail in any particular area?