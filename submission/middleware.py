# submission/middleware.py
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class SubmissionAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log submission access
        if request.path.startswith('/submission/') and request.user.is_authenticated:
            try:
                submission_id = request.resolver_match.kwargs.get('submission_id')
                if submission_id:
                    logger.info(
                        f"User {request.user.username} accessed submission {submission_id} "
                        f"at {timezone.now()}"
                    )
            except Exception as e:
                logger.error(f"Error in SubmissionAccessMiddleware: {str(e)}")
                
        return response