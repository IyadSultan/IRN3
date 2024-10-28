# submission/utils.py

from users.models import UserProfile  # Adjust the import based on your users app

def has_edit_permission(user, submission):
    if submission.primary_investigator == user:
        return True
    if submission.research_assistants.filter(user=user, can_edit=True).exists():
        return True
    if submission.coinvestigators.filter(user=user, can_edit=True).exists():
        return True
    return False

def check_researcher_documents(submission):
    from django.utils import timezone
    all_good = True
    missing_docs = []
    investigator_ids = [submission.primary_investigator.id] + list(submission.coinvestigators.values_list('user__id', flat=True))
    for user_id in investigator_ids:
        try:
            user_profile = UserProfile.objects.get(user__id=user_id)
            # Check for required documents
            if not user_profile.gcp_certificate or user_profile.gcp_certificate_is_expired():
                all_good = False
                missing_docs.append(f"{user_profile.user.get_full_name()}'s GCP Certificate")
            # Add other checks as needed (e.g., consent training, CV)
        except UserProfile.DoesNotExist:
            all_good = False
            missing_docs.append(f"UserProfile for user ID {user_id} does not exist.")
    return all_good, missing_docs
