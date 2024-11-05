# review/urls.py

from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('', views.review_dashboard, name='review_dashboard'),
    path('create/<int:submission_id>/', views.create_review_request, name='create_review_request'),
    path('submit/<int:review_request_id>/', views.submit_review, name='submit_review'),
    path('dashboard/', views.review_dashboard, name='review_dashboard'),
    path('review/<int:review_id>/', views.view_review, name='view_review'),
    path('review/<int:review_id>/submit/', views.submit_review, name='submit_review'),
    path('review/<int:review_id>/extension/', views.request_extension, name='request_extension'),
    path('review/<int:review_id>/decline/', views.decline_review, name='decline_review'),
    
]