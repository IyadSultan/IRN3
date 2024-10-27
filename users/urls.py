# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),
    path('upload_document/', views.upload_document, name='upload_document'),
    path('view_documents/', views.view_documents, name='view_documents'),
    path('display_document/<int:document_id>/', views.display_document, name='display_document'),
]
