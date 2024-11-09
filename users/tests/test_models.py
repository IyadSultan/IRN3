# users/tests/test_models.py
import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from users.models import UserProfile

pytestmark = pytest.mark.django_db

def test_user_creation():
    """Test basic user creation"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    profile = UserProfile.objects.get(user=user)
    profile.full_name = 'Test User'
    profile.save()
    
    assert User.objects.filter(username='testuser').exists()
    assert user.email == 'test@example.com'
    assert profile.full_name == 'Test User'

def test_profile_validation():
    """Test profile validation rules"""
    user = User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123',
        first_name='John',
        last_name='Doe'
    )
    profile = UserProfile.objects.get(user=user)
    
    # Test valid full name
    profile.full_name = 'John Doe'
    profile.save()
    assert profile.full_name == 'John Doe'
    
    # Test invalid full name (should raise ValidationError)
    with pytest.raises(ValidationError) as excinfo:
        profile.full_name = 'John'  # Only one name
        profile.full_clean()
    assert "Full name must contain at least two names" in str(excinfo.value)

def test_profile_auto_creation():
    """Test that profile is automatically created with proper full name"""
    user = User.objects.create_user(
        username='testuser3',
        email='test3@example.com',
        password='testpass123',
        first_name='Jane',
        last_name='Smith'
    )
    profile = UserProfile.objects.get(user=user)
    profile.full_name = 'Jane Smith'
    profile.save()
    
    assert UserProfile.objects.filter(user=user).exists()
    assert profile.full_name == 'Jane Smith'

def test_profile_required_fields():
    """Test required fields validation"""
    user = User.objects.create_user(
        username='testuser4',
        email='test4@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User Four'
    )
    
    profile = UserProfile.objects.get(user=user)
    profile.full_name = 'Test User Four'
    profile.role = 'KHCC investigator'
    profile.institution = 'King Hussein Cancer Center'
    
    # Should raise error because khcc_employee_number is missing
    with pytest.raises(ValidationError) as excinfo:
        profile.full_clean()
    assert "Employee number is required for KHCC investigators" in str(excinfo.value)
    
    profile.khcc_employee_number = 'EMP123'
    profile.full_clean()  # Should not raise an error
    profile.save()
    
    saved_profile = UserProfile.objects.get(user=user)
    assert saved_profile.khcc_employee_number == 'EMP123'
    assert saved_profile.role == 'KHCC investigator'

def test_profile_institution_validation():
    """Test institution validation for KHCC investigators"""
    user = User.objects.create_user(
        username='testuser5',
        email='test5@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User Five'
    )
    
    profile = UserProfile.objects.get(user=user)
    profile.full_name = 'Test User Five'
    profile.save()  # Save first with valid data
    
    # Update with invalid data
    profile.role = 'KHCC investigator'
    profile.khcc_employee_number = 'EMP123'
    profile.institution = 'Other Institution'
    
    with pytest.raises(ValidationError) as excinfo:
        profile.full_clean()
    assert "KHCC investigators must be from King Hussein Cancer Center" in str(excinfo.value)
    
    # Test that it works with correct institution
    profile.institution = 'King Hussein Cancer Center'
    profile.full_clean()  # Should not raise error
    profile.save()
    
    saved_profile = UserProfile.objects.get(user=user)
    assert saved_profile.institution == 'King Hussein Cancer Center'
    assert saved_profile.role == 'KHCC investigator'
    assert saved_profile.khcc_employee_number == 'EMP123'

def test_non_khcc_profile_validation():
    """Test validation for non-KHCC investigators"""
    user = User.objects.create_user(
        username='testuser6',
        email='test6@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User Six'
    )
    
    profile = UserProfile.objects.get(user=user)
    profile.full_name = 'Test User Six'
    profile.role = 'Non-KHCC investigator'
    profile.institution = 'Other Institution'
    profile.full_clean()  # Should not raise error
    profile.save()
    
    saved_profile = UserProfile.objects.get(user=user)
    assert saved_profile.institution == 'Other Institution'
    assert saved_profile.role == 'Non-KHCC investigator'