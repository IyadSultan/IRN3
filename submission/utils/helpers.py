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

    def check_user_documents(profile, role_key, user_name):
        """Helper function to check documents for a user"""
        missing = []
        if not profile.has_valid_gcp:
            missing.append('GCP Certificate (Expired or Missing)')
        if not profile.has_qrc:
            missing.append('QRC Certificate')
        if not profile.has_ctc:
            missing.append('CTC Certificate')
        if not profile.has_cv:
            missing.append('CV')
        if missing:
            # Use a unique key for each user by combining role and name
            key = f"{role_key}: {user_name}"
            missing_documents[key] = {
                'name': user_name,
                'documents': missing
            }

    # Check primary investigator's documents
    pi_profile = submission.primary_investigator.userprofile
    check_user_documents(pi_profile, 'Primary Investigator', pi_profile.full_name)

    # Check co-investigators' documents
    for coinv in submission.coinvestigators.all():
        coinv_profile = coinv.user.userprofile
        check_user_documents(coinv_profile, 'Co-Investigator', coinv_profile.full_name)

    # Check research assistants' documents
    for ra in submission.research_assistants.all():
        ra_profile = ra.user.userprofile
        check_user_documents(ra_profile, 'Research Assistant', ra_profile.full_name)

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