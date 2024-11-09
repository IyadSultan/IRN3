# users/tests/conftest.py
import pytest
from django.contrib.auth.models import User
from users.models import UserProfile

@pytest.fixture
def test_password():
    return 'testpass123'

@pytest.fixture
def test_full_name():
    return 'Test User'

@pytest.fixture
def test_user(db, test_password, test_full_name):
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password=test_password,
        first_name='Test',
        last_name='User'
    )
    profile = UserProfile.objects.get(user=user)
    profile.full_name = test_full_name
    profile.save()
    return user

@pytest.fixture
def test_profile(test_user):
    return UserProfile.objects.get(user=test_user)

@pytest.fixture
def valid_user_data():
    return {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'testpass123',
        'first_name': 'New',
        'last_name': 'User'
    }

@pytest.fixture
def valid_profile_data():
    return {
        'full_name': 'New User',
        'institution': 'Test Institution',
        'mobile': '+962777777777',
        'title': 'Researcher'
    }