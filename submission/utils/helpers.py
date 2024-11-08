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
    """Check if all required documents are present for researchers."""
    missing_documents = []
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
    return submission.study_type.forms.filter(
        order__lt=current_form.order
    ).order_by('-order').first()