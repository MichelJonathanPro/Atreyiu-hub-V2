from django.utils import timezone
from .models import UserSession

class UserSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.session.session_key:
            try:
                user_session = UserSession.objects.get(
                    user=request.user, 
                    session_key=request.session.session_key
                )
                # Update last_activity if it's been more than 5 minutes
                if (timezone.now() - user_session.last_activity).total_seconds() > 300:
                    user_session.last_activity = timezone.now()
                    user_session.save(update_fields=['last_activity'])
            except UserSession.DoesNotExist:
                pass
                
        response = self.get_response(request)
        return response
