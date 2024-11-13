# Create a new file: feedback/urls.py

from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('confirmation/', views.feedback_confirmation, name='feedback_confirmation'),
]