from django.urls import path
from .views import (
    # Dashboard Views
    ReviewDashboardView,
    osar_dashboard,
    irb_dashboard,
    rc_dashboard,
    
    # Submission Views
    ReviewSummaryView,
    SubmissionVersionsView,
    ToggleSubmissionVisibilityView,
    UpdateSubmissionStatusView,
    AssignKHCCNumberView,
    ProcessSubmissionDecisionView,
    view_notepad,
    
    # Review Process Views
    CreateReviewRequestView,
    SubmitReviewView,
    ViewReviewView,
    RequestExtensionView,
    DeclineReviewView,
    download_review_pdf,
)
from submission.views import user_autocomplete

app_name = 'review'

urlpatterns = [
    # Dashboard URLs
    path('', ReviewDashboardView.as_view(), 
         name='review_dashboard'),
    path('osar-dashboard/', osar_dashboard, 
         name='osar_dashboard'),
    path('irb-dashboard/', irb_dashboard, 
         name='irb_dashboard'),
    path('rc-dashboard/', rc_dashboard, 
         name='rc_dashboard'),

    # Submission Management URLs
    path('submission/<int:submission_id>/summary/', 
         ReviewSummaryView.as_view(), 
         name='review_summary'),
    path('submission/<int:submission_id>/versions/', 
         SubmissionVersionsView.as_view(), 
         name='submission_versions'),
    path('submission/<int:submission_id>/toggle-visibility/', 
         ToggleSubmissionVisibilityView.as_view(), 
         name='toggle_visibility'),
    path('submission/<int:submission_id>/update-status/', 
         UpdateSubmissionStatusView.as_view(), 
         name='update_status'),
    path('submission/<int:submission_id>/assign-irb/', 
         AssignKHCCNumberView.as_view(), 
         name='assign_irb'),
    path('submission/<int:submission_id>/process-decision/', 
         ProcessSubmissionDecisionView.as_view(), 
         name='process_submission_decision'),
    path('submission/<int:submission_id>/notepad/<str:notepad_type>/', 
         view_notepad, 
         name='view_notepad'),

    # Review Process URLs
    path('create/<int:submission_id>/', 
         CreateReviewRequestView.as_view(), 
         name='create_review_request'),
    path('submit/<int:review_request_id>/', 
         SubmitReviewView.as_view(), 
         name='submit_review'),
    path('review/<int:review_request_id>/', 
         ViewReviewView.as_view(), 
         name='view_review'),
    path('review/<int:review_request_id>/extension/', 
         RequestExtensionView.as_view(), 
         name='request_extension'),
    path('review/<int:review_request_id>/decline/', 
         DeclineReviewView.as_view(), 
         name='decline_review'),
    path('review/<int:review_request_id>/pdf/', 
         download_review_pdf, 
         name='download_review_pdf'),

    # Utility URLs
    path('user-autocomplete/', 
         user_autocomplete, 
         name='user-autocomplete'),
]