# submission/utils.py

from users.models import UserProfile  # Adjust the import based on your users app
from .models import CoInvestigator, ResearchAssistant
from forms_builder.models import DynamicForm


def has_edit_permission(user, submission):
    # Check if user is primary investigator
    if user == submission.primary_investigator:
        return True

    # Check if user is a co-investigator with edit permission
    if submission.coinvestigators.filter(user=user, can_edit=True).exists():
        return True

    # Check if user is a research assistant with edit permission
    if submission.research_assistants.filter(user=user, can_edit=True).exists():
        return True

    return False


def check_researcher_documents(submission):
    """Check documents for all researchers involved in the submission"""
    missing_documents = {}

    # Check primary investigator's documents
    pi_profile = submission.primary_investigator.userprofile
    pi_missing = []
    if pi_profile.is_gcp_expired:
        pi_missing.append('GCP Certificate')
    if pi_profile.is_qrc_expired:
        pi_missing.append('QRC Certificate')
    if pi_profile.is_ctc_expired:
        pi_missing.append('CTC Certificate')
    if pi_profile.is_cv_missing:
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
        if coinv_profile.is_gcp_expired:
            coinv_missing.append('GCP Certificate')
        if coinv_profile.is_qrc_expired:
            coinv_missing.append('QRC Certificate')
        if coinv_profile.is_ctc_expired:
            coinv_missing.append('CTC Certificate')
        if coinv_profile.is_cv_missing:
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
        if ra_profile.is_gcp_expired:
            ra_missing.append('GCP Certificate')
        if ra_profile.is_qrc_expired:
            ra_missing.append('QRC Certificate')
        if ra_profile.is_ctc_expired:
            ra_missing.append('CTC Certificate')
        if ra_profile.is_cv_missing:
            ra_missing.append('CV')
        if ra_missing:
            missing_documents[f'Research Assistant: {ra.user.get_full_name()}'] = {
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
    dynamic_forms = list(submission.study_type.forms.order_by('order'))
    try:
        index = dynamic_forms.index(current_form)
        return dynamic_forms[index - 1] if index - 1 >= 0 else None
    except ValueError:
        return None
