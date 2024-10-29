# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

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

def validate_full_name(value):
    names = value.strip().split()
    if len(names) < 3:
        raise ValidationError('Full name must contain at least three names.')

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
    full_name = models.CharField(
        max_length=255,
        default='',
        help_text='Full name (at least three names required)'
    )

    # Add property methods to access certificates
    @property
    def gcp_certificate(self):
        return self.user.documents.filter(document_type='GCP').first()

    @property
    def qrc_certificate(self):
        return self.user.documents.filter(document_type='QRC').first()

    @property
    def ctc_certificate(self):
        return self.user.documents.filter(document_type='CTC').first()

    @property
    def cv_document(self):
        return self.user.documents.filter(document_type='CV').first()

    @property
    def is_gcp_expired(self):
        cert = self.gcp_certificate
        if cert and cert.expiry_date:
            return cert.expiry_date <= timezone.now().date()
        return True  # If no certificate exists, consider it expired

    @property
    def is_qrc_expired(self):
        cert = self.qrc_certificate
        if cert and cert.expiry_date:
            return cert.expiry_date <= timezone.now().date()
        return True

    @property
    def is_ctc_expired(self):
        cert = self.ctc_certificate
        if cert and cert.expiry_date:
            return cert.expiry_date <= timezone.now().date()
        return True

    @property
    def is_cv_missing(self):
        return not self.cv_document

    @property
    def has_valid_gcp(self):
        return not self.is_gcp_expired

    @property
    def has_valid_qrc(self):
        return not self.is_qrc_expired

    @property
    def has_valid_ctc(self):
        return not self.is_ctc_expired

    @property
    def has_valid_cv(self):
        return not self.is_cv_missing

    @property
    def missing_documents(self):
        missing = []
        if self.is_gcp_expired:
            missing.append('GCP Certificate')
        if self.is_qrc_expired:
            missing.append('QRC Certificate')
        if self.is_ctc_expired:
            missing.append('CTC Certificate')
        if self.is_cv_missing:
            missing.append('CV')
        return missing

    @property
    def has_all_valid_documents(self):
        return len(self.missing_documents) == 0

    def __str__(self):
        return self.user.username

    def clean(self):
        """Validate that the full name contains at least three parts."""
        if self.full_name.strip():  # Only validate if not empty
            validate_full_name(self.full_name)

    def save(self, *args, **kwargs):
        # If full_name is not set, try to construct it from user's first and last name
        if not self.full_name and self.user:
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        super().save(*args, **kwargs)

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

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False  # If no expiry date, consider it not expired

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None

    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"

# users/models.py

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Create or update the UserProfile when User is saved"""
    if created:
        # Create new profile
        UserProfile.objects.create(
            user=instance,
            full_name=f"{instance.first_name} {instance.last_name}".strip()
        )
    else:
        # Update existing profile
        if hasattr(instance, 'userprofile'):
            profile = instance.userprofile
            if not profile.full_name:
                profile.full_name = f"{instance.first_name} {instance.last_name}".strip()
            profile.save()
