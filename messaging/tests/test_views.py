# messaging/tests/test_views.py

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from messaging.models import Message

User = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def authenticated_user():
    return User.objects.create_user(
        username='testuser',
        email='test@test.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def authenticated_client(client, authenticated_user):
    client.login(username='testuser', password='testpass123')
    return client

def test_inbox_view(authenticated_client):
    """Test inbox view"""
    response = authenticated_client.get(reverse('messaging:inbox'))
    assert response.status_code == 200
    assert 'messages' in response.context

def test_compose_message_get(authenticated_client):
    """Test compose message view - GET"""
    response = authenticated_client.get(reverse('messaging:compose_message'))
    assert response.status_code == 200
    assert 'form' in response.context

def test_compose_message_post(authenticated_client, authenticated_user):
    """Test compose message view - POST"""
    recipient = User.objects.create_user(
        username='recipient',
        email='recipient@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Recipient'
    )
    
    data = {
        'subject': 'Test Subject',
        'body': 'Test Body',
        'recipients': [recipient.id],
    }
    
    response = authenticated_client.post(reverse('messaging:compose_message'), data)
    assert response.status_code == 302  # Redirect after successful creation
    
    # Verify message was created
    message = Message.objects.filter(subject='Test Subject').first()
    assert message is not None
    assert message.sender == authenticated_user
    assert recipient in message.recipients.all()

def test_view_message(authenticated_client, authenticated_user):
    """Test viewing a specific message"""
    message = Message.objects.create(
        sender=authenticated_user,
        subject='Test Subject',
        body='Test Body'
    )
    message.recipients.add(authenticated_user)
    
    response = authenticated_client.get(
        reverse('messaging:view_message', kwargs={'message_id': message.id})
    )
    assert response.status_code == 200
    assert response.context['message'] == message