# submission/urls.py

from django.urls import path
from . import views

app_name = 'submission'

urlpatterns = [
    path('start-submission/<int:submission_id>/', views.start_submission, name='start_submission_with_id'),
    path('start-submission/', views.start_submission, name='start_submission'),
    path('edit-submission/<int:submission_id>/', views.edit_submission, name='edit_submission'),
    path('add-research-assistant/<int:submission_id>/', views.add_research_assistant, name='add_research_assistant'),
    path('add-coinvestigator/<int:submission_id>/', views.add_coinvestigator, name='add_coinvestigator'),
    path('submission-form/<int:submission_id>/<int:form_id>/', views.submission_form, name='submission_form'),
    path('submission-review/<int:submission_id>/', views.submission_review, name='submission_review'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-autocomplete/', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    path('download-pdf/<int:submission_id>/', views.download_submission_pdf, name='download_submission_pdf'),
    path('update-coinvestigator-order/<int:submission_id>/', views.update_coinvestigator_order, name='update_coinvestigator_order'),
    # ... other URL patterns ...
]
