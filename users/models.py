# users/models.py

from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('KHCC investigator', 'KHCC investigator'),
    ('Non-KHCC investigator', 'Non-KHCC investigator'),
    ('Research Assistant/Coordinator', 'Research Assistant/Coordinator'),
    ('OSAR head', 'OSAR head'),
    ('OSAR coordinator', 'OSAR coordinator'),
    ('IRB chair', 'IRB chair'),
    ('RC coordinator', 'RC coordinator'),
    ('IRB member', 'IRB member'),
    ('RC chair', 'RC chair'),
    ('RC member', 'RC member'),
    ('RC coordinator', 'RC coordinator'),
    ('AHARPP Head', 'AHARPP Head'),
    ('System administrator', 'System administrator'),
    ('CEO', 'CEO'),
    ('CMO', 'CMO'),
    ('AIDI Head', 'AIDI Head'),
    ('Grant Management Officer', 'Grant Management Officer'),
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
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)

    def __str__(self):
        return self.user.username

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

    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"

# users/models.py

from django.db.models.signals import post_save
from django.dispatch import receiver

# This function listens for the post_save signal from the User model.
# When a User instance is created, it automatically creates a corresponding UserProfile.
# If the User instance is updated, it saves the existing UserProfile associated with that User.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()
