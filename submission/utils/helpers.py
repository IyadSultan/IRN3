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
        
    return False

def check_researcher_documents(submission):
    """Check if all required documents are present for researchers."""
    missing_documents = []
    return missing_documents

def get_next_form(submission, current_form):
    """Get the next form in the submission process."""
    return submission.study_type.forms.filter(
        order__gt=current_form.order
    ).order_by('order').first()

def get_previous_form(submission, current_form):
    """Get the previous form in the submission process."""
    return submission.study_type.forms.filter(
        order__lt=current_form.order
    ).order_by('-order').first()