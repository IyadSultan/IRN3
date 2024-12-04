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
    path('user-autocomplete/', views.user_autocomplete, name='user-autocomplete'),
    path('download-pdf/<int:submission_id>/', views.download_submission_pdf, name='download_submission_pdf'),
    path('download-pdf/<int:submission_id>/<int:version>/', views.download_submission_pdf, name='download_submission_pdf_version'),
    path('update-coinvestigator-order/<int:submission_id>/', views.update_coinvestigator_order, name='update_coinvestigator_order'),
    path('document-delete/<int:submission_id>/<int:document_id>/', views.document_delete, name='document_delete'),
    path('version-history/<int:submission_id>/', views.version_history, name='version_history'),
    path('<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('<int:submission_id>/version/<int:version_number>/', views.view_version, name='view_version'),
    path('compare-version/<int:submission_id>/<int:version1>/<int:version2>/', 
         views.compare_version, 
         name='compare_version'),
    path('investigator-form/<int:submission_id>/<int:form_id>/', views.investigator_form, name='investigator_form'),
    path('check-form-status/<int:submission_id>/', views.check_form_status, name='check_form_status'),
    path('archived/', views.archived_dashboard, name='archived_dashboard'),
    path('archive/<int:submission_id>/', views.archive_submission, name='archive_submission'),
    path('unarchive/<int:submission_id>/', views.unarchive_submission, name='unarchive_submission'),
    path('view/<int:submission_id>/', views.view_submission, name='view_submission'),
    path('submission/<int:submission_id>/withdraw/', views.study_withdrawal, name='study_withdrawal'),
    path('submission/<int:submission_id>/progress/', views.progress_report, name='progress_report'),
    path('submission/<int:submission_id>/amendment/', views.study_amendment, name='study_amendment'),
    path('submission/<int:submission_id>/closure/', views.study_closure, name='study_closure'),
    path('submission/<int:submission_id>/actions/', views.submission_actions, name='submission_actions'),
    path('download-action-pdf/<int:submission_id>/<int:action_id>/', 
         views.download_action_pdf, 
         name='download_action_pdf'),

    # urls.py
    path('action/<int:action_id>/pdf/', 
         views.download_action_pdf, 
         name='download_action_pdf'),
]

