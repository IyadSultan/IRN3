# submission/urls.py

from django.urls import path
from . import views

app_name = 'submission'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start_submission/', views.start_submission, name='start_submission'),
    path('submission/<int:submission_id>/edit/', views.edit_submission, name='edit_submission'),
    path('submission/<int:submission_id>/download_pdf/', views.download_submission_pdf, name='download_submission_pdf'),  # Changed this line
    path('user-autocomplete/', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    path('<int:submission_id>/research-assistant/', views.add_research_assistant, name='add_research_assistant'),
    path('<int:submission_id>/coinvestigator/', views.add_coinvestigator, name='add_coinvestigator'),
    path('<int:submission_id>/forms/', views.submission_forms, name='submission_forms'),
]
