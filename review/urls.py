from django.urls import path
from .views import (
    ReviewDashboardView,
    IRBDashboardView,
    RCDashboardView,
    ToggleSubmissionVisibilityView,
    UpdateSubmissionStatusView,
    CreateReviewRequestView,
    SubmitReviewView,
    ViewReviewView,
    RequestExtensionView,
    DeclineReviewView,
    ReviewSummaryView,
    ProcessIRBDecisionView,
    SubmissionVersionsView,
    download_review_pdf,
    AssignIRBNumberView,
    osar_dashboard,
    irb_dashboard,
    rc_dashboard
)
from submission.views import user_autocomplete

app_name = 'review'

urlpatterns = [
    path('', ReviewDashboardView.as_view(), name='review_dashboard'),

    path(
        'submission/<int:submission_id>/toggle-visibility/',
        ToggleSubmissionVisibilityView.as_view(),
        name='toggle_visibility'
    ),
    path(
        'submission/<int:submission_id>/update-status/',
        UpdateSubmissionStatusView.as_view(),
        name='update_status'
    ),
    path('create/<int:submission_id>/', CreateReviewRequestView.as_view(), name='create_review_request'),
    path('submit/<int:review_request_id>/', SubmitReviewView.as_view(), name='submit_review'),
    path('review/<int:review_request_id>/', ViewReviewView.as_view(), name='view_review'),
    path('review/<int:review_request_id>/extension/', RequestExtensionView.as_view(), name='request_extension'),
    path('review/<int:review_request_id>/decline/', DeclineReviewView.as_view(), name='decline_review'),
    path('submission/<int:submission_id>/summary/', ReviewSummaryView.as_view(), name='review_summary'),
    path('submission/<int:submission_id>/decision/', ProcessIRBDecisionView.as_view(), name='process_decision'),
    path('user-autocomplete/', user_autocomplete, name='user-autocomplete'),
    path('submission/<int:submission_id>/versions/', SubmissionVersionsView.as_view(), name='submission_versions'),
    path('review/<int:review_request_id>/pdf/', download_review_pdf, name='download_review_pdf'),
    path('submission/<int:submission_id>/assign-irb/', AssignIRBNumberView.as_view(), name='assign_irb'),


    path('irb-dashboard/', irb_dashboard, name='irb_dashboard'),
    path('rc-dashboard/', rc_dashboard, name='rc_dashboard'),
    path('osar-dashboard/', osar_dashboard, name='osar_dashboard'),
    path('submission/<int:submission_id>/toggle-visibility/',
    ToggleSubmissionVisibilityView.as_view(),
    name='toggle_visibility'
),



]
