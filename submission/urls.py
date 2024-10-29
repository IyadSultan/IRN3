# submission/urls.py

from django.urls import path
from . import views

app_name = 'submission'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start_submission/', views.start_submission, name='start_submission'),
    path('start_submission/<int:submission_id>/', views.start_submission, name='start_submission'),
    path('user-autocomplete/', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    path('submission/<int:submission_id>/edit/', views.start_submission, name='edit_submission'),
    path('submission/<int:submission_id>/download_pdf/', views.download_submission_pdf, name='download_submission_pdf'),
    path('<int:submission_id>/research-assistant/', views.add_research_assistant, name='add_research_assistant'),
    path('<int:submission_id>/coinvestigator/', views.add_coinvestigator, name='add_coinvestigator'),
    path('<int:submission_id>/forms/', views.submission_forms, name='submission_forms'),
    path('<int:submission_id>/review/', views.submission_review, name='submission_review'),
    path('<int:submission_id>/update-coinvestigator-order/', 
         views.update_coinvestigator_order, 
         name='update_coinvestigator_order'),
]
