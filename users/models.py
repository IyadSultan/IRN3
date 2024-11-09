# users/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from django.core.validators import EmailValidator, RegexValidator
from iRN.constants import USER_ROLE_CHOICES

class Role(models.Model):
    """Role model for managing user roles"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name

class Group(models.Model):
    """Group model for user permissions"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

def validate_full_name(value):
    """Validate full name format"""
    names = value.strip().split()
    if len(names) < 2:
        raise ValidationError('Full name must contain at least two names.')
    if not all(name.isalpha() for name in names):
        raise ValidationError('Names should only contain letters.')
    if any(len(name) < 2 for name in names):
        raise ValidationError('Each name should be at least 2 characters long.')

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    institution = models.CharField(
        max_length=255,
        default='King Hussein Cancer Center'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        default='',
        validators=[phone_regex]
    )
    khcc_employee_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]+$',
                message='Employee number can only contain letters and numbers.'
            )
        ]
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=50,
        choices=USER_ROLE_CHOICES,
        blank=True,
        null=True
    )
    groups = models.ManyToManyField(
        Group,
        related_name='user_profiles',
        blank=True
    )
    photo = models.ImageField(
        upload_to='photos/',
        blank=True,
        null=True
    )
    is_approved = models.BooleanField(default=False)
    full_name = models.CharField(
        max_length=255,
        default='',
        help_text='Full name (at least two names required)',
        validators=[validate_full_name]
    )

    class Meta:
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['is_approved']),
            models.Index(fields=['role'])
        ]

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    def clean(self):
        """Validate model fields"""
        super().clean()
        
        if self.role == 'KHCC investigator':
            # Validate employee number
            if not self.khcc_employee_number:
                raise ValidationError({
                    'khcc_employee_number': 'Employee number is required for KHCC investigators.'
                })
                
            # Validate institution
            if self.institution.lower() != 'king hussein cancer center':
                raise ValidationError({
                    'institution': 'KHCC investigators must be from King Hussein Cancer Center'
                })

        if self.full_name:
            validate_full_name(self.full_name)

    def save(self, *args, **kwargs):
        """Custom save method with additional logic"""
        if not self.full_name and self.user:
            self.full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        
        # Only run full_clean if it's a new object or specific fields have changed
        if not self.pk or self.has_changed:
            self.full_clean()
            
        super().save(*args, **kwargs)

    @property
    def has_changed(self):
        """Check if important fields have changed"""
        if not self.pk:
            return True
            
        original = UserProfile.objects.get(pk=self.pk)
        fields_to_check = ['full_name', 'role', 'institution', 'khcc_employee_number']
        
        return any(getattr(self, field) != getattr(original, field) for field in fields_to_check)

    def is_in_group(self, group_name):
        return self.groups.filter(name=group_name).exists()

    @property
    def is_irb_member(self):
        return self.is_in_group('IRB Member')

    @property
    def is_research_council_member(self):
        return self.is_in_group('Research Council Member')

    @property
    def is_head_of_irb(self):
        return self.is_in_group('Head of IRB')

    @property
    def is_osar_admin(self):
        return self.is_in_group('OSAR Admin')

    @property
    def has_valid_gcp(self):
        today = timezone.now().date()
        return self.user.documents.filter(
            document_type='GCP',
            expiry_date__gt=today
        ).exists()

    @property
    def has_qrc(self):
        return self.user.documents.filter(document_type='QRC').exists()

    @property
    def has_ctc(self):
        return self.user.documents.filter(document_type='CTC').exists()

    @property
    def has_cv(self):
        return self.user.documents.filter(document_type='CV').exists()

class Document(models.Model):
    """Document model for user certificates and files"""
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

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['document_type', 'expiry_date'])
        ]

    def __str__(self):
        display_name = self.other_document_name if self.document_type == 'Other' else self.get_document_type_display()
        return f"{self.user.username} - {display_name}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days
        return None

    @property
    def get_name(self):
        """Return the document name for display"""
        if self.document_type == 'Other' and self.other_document_name:
            return self.other_document_name
        return self.get_document_type_display()

class SystemSettings(models.Model):
    """System-wide settings model"""
    system_email = models.EmailField(
        default='aidi@khcc.jo',
        help_text='System email address for automated messages'
    )
    system_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_settings',
        help_text='System user account for automated actions'
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
        return User.objects.filter(is_superuser=True).first()