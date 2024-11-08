from django.urls import path
from .views import (
    ReviewDashboardView,
    CreateReviewRequestView,
    SubmitReviewView,
    ViewReviewView,
    RequestExtensionView,
    DeclineReviewView,
    ReviewSummaryView,
    ProcessIRBDecisionView,
    SubmissionVersionsView,
    download_review_pdf,
)
from submission.views import user_autocomplete

app_name = 'review'

urlpatterns = [
    path('', ReviewDashboardView.as_view(), name='review_dashboard'),
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

]
