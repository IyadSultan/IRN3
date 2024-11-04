# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache

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
    full_name = models.CharField(
        max_length=255,
        default='',
        help_text='Full name (at least three names required)'
    )

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

    @property
    def has_valid_gcp(self):
        """Check if user has a valid (non-expired) GCP certificate"""
        today = timezone.now().date()
        return self.user.documents.filter(
            document_type='GCP',
            expiry_date__gt=today
        ).exists()

    @property
    def has_qrc(self):
        """Check if user has uploaded a QRC certificate"""
        return self.user.documents.filter(
            document_type='QRC'
        ).exists()

    @property
    def has_ctc(self):
        """Check if user has uploaded a CTC certificate"""
        return self.user.documents.filter(
            document_type='CTC'
        ).exists()

    @property
    def has_cv(self):
        """Check if user has uploaded a CV"""
        return self.user.documents.filter(
            document_type='Other',
            other_document_name__icontains='CV'
        ).exists()

    @property
    def is_gcp_expired(self):
        """Check if GCP is expired or missing"""
        today = timezone.now().date()
        latest_gcp = self.user.documents.filter(
            document_type='GCP'
        ).order_by('-expiry_date').first()
        if not latest_gcp or not latest_gcp.expiry_date:
            return True
        return latest_gcp.expiry_date <= today

    # Helper properties for template usage
    @property
    def is_qrc_missing(self):
        return not self.has_qrc

    @property
    def is_ctc_missing(self):
        return not self.has_ctc

    @property
    def is_cv_missing(self):
        return not self.has_cv

class Document(models.Model):
    DOCUMENT_CHOICES = [
        ('GCP', 'Good Clinical Practice Certificate'),
        ('QRC', 'Qualitative Record Certificate'),
        ('CTC', 'Consent Training Certificate'),
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

    @property
    def is_missing(self):
        return not self.file  # Check if the document file is missing

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

class SystemSettings(models.Model):
    system_email = models.EmailField(
        default='aidi@khcc.jo',
        help_text='System email address used for automated messages'
    )
    system_user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings',
        help_text='User account to be used for system messages'
    )
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def save(self, *args, **kwargs):
        cache.delete('system_settings')
        super().save(*args, **kwargs)
        
    @classmethod
    def get_system_user(cls):
        settings = cls.objects.first()
        if settings and settings.system_user:
            return settings.system_user
        # Fallback to first superuser if no system user is set
        return User.objects.filter(is_superuser=True).first()


from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']