# submission/utils/helpers.py

def has_edit_permission(user, submission):

    """Check if user has permission to edit the submission."""
    if user == submission.primary_investigator:
        return True
        
    # Check if user is a co-investigator with edit permission
    if submission.coinvestigators.filter(user=user, can_edit=True).exists():
        return True
        
    # Check if user is a research assistant with edit permission
    if submission.research_assistants.filter(user=user, can_edit=True).exists():
        return True
    
    # Check if user is the one who requested the review
    if submission.review_requests.filter(requested_by=user).first() or\
    submission.review_requests.filter(requested_to=user).first():
        return True

        
    return False
def check_researcher_documents(submission):
    """Check documents for all researchers involved in the submission"""
    missing_documents = {}

    # Check primary investigator's documents
    pi_profile = submission.primary_investigator.userprofile
    pi_missing = []
    if not pi_profile.has_valid_gcp:
        pi_missing.append('GCP Certificate (Expired or Missing)')
    if not pi_profile.has_qrc:
        pi_missing.append('QRC Certificate')
    if not pi_profile.has_ctc:
        pi_missing.append('CTC Certificate')
    if not pi_profile.has_cv:
        pi_missing.append('CV')
    if pi_missing:
        missing_documents['Primary Investigator'] = {
            'name': pi_profile.full_name,
            'documents': pi_missing
        }

    # Check co-investigators' documents
    for coinv in submission.coinvestigators.all():
        coinv_profile = coinv.user.userprofile
        coinv_missing = []
        if not coinv_profile.has_valid_gcp:
            coinv_missing.append('GCP Certificate (Expired or Missing)')
        if not coinv_profile.has_qrc:
            coinv_missing.append('QRC Certificate')
        if not coinv_profile.has_ctc:
            coinv_missing.append('CTC Certificate')
        if not coinv_profile.has_cv:
            coinv_missing.append('CV')
        if coinv_missing:
            missing_documents[f'Co-Investigator: {coinv.role_in_study}'] = {
                'name': coinv_profile.full_name,
                'documents': coinv_missing
            }

    # Check research assistants' documents
    for ra in submission.research_assistants.all():
        ra_profile = ra.user.userprofile
        ra_missing = []
        if not ra_profile.has_valid_gcp:
            ra_missing.append('GCP Certificate (Expired or Missing)')
        if not ra_profile.has_qrc:
            ra_missing.append('QRC Certificate')
        if not ra_profile.has_ctc:
            ra_missing.append('CTC Certificate')
        if not ra_profile.has_cv:
            ra_missing.append('CV')
        if ra_missing:
            missing_documents[f'Research Assistant'] = {
                'name': ra_profile.full_name,
                'documents': ra_missing
            }

    return missing_documents


def get_next_form(submission, current_form):
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index + 1] if index + 1 < len(dynamic_forms) else None
    except ValueError:
        return None


def get_previous_form(submission, current_form):
    """Get the previous form in the submission process."""
    # Get all forms for this study type in correct order
    study_forms = list(submission.study_type.forms.order_by('order'))
    
    try:
        # Find current form's index
        current_index = study_forms.index(current_form)
        
        # If we're not at the first form, return the previous one
        if current_index > 0:
            return study_forms[current_index - 1]
    except ValueError:
        pass
        
    return None