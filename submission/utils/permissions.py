# submission/utils/permissions.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def check_submission_permission(action_type):
    """
    Decorator to check submission permissions for different action types.
    action_type can be: 'edit', 'submit', 'view_communications'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, submission_id, *args, **kwargs):
            from submission.models import Submission
            
            try:
                submission = Submission.objects.get(pk=submission_id)
                
                # Primary Investigator has all permissions
                if request.user == submission.primary_investigator:
                    return view_func(request, submission_id, *args, **kwargs)
                
                # Check Co-Investigator permissions
                coinv = submission.coinvestigators.filter(user=request.user).first()
                if coinv:
                    if action_type == 'edit' and coinv.can_edit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'submit' and coinv.can_submit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'view_communications' and coinv.can_view_communications:
                        return view_func(request, submission_id, *args, **kwargs)
                
                # Check Research Assistant permissions
                ra = submission.research_assistants.filter(user=request.user).first()
                if ra:
                    if action_type == 'edit' and ra.can_edit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'submit' and ra.can_submit:
                        return view_func(request, submission_id, *args, **kwargs)
                    elif action_type == 'view_communications' and ra.can_view_communications:
                        return view_func(request, submission_id, *args, **kwargs)
                
                messages.error(request, f"You don't have permission to {action_type} this submission.")
                return redirect('submission:dashboard')
                
            except Submission.DoesNotExist:
                messages.error(request, "Submission not found.")
                return redirect('submission:dashboard')
                
        return _wrapped_view
    return decorator