from django.shortcuts import redirect
from django.urls import reverse
from social_core.exceptions import AuthAlreadyAssociated
import logging

logger = logging.getLogger(__name__)

class SocialAuthExceptionMiddleware:
    """
    Middleware to handle Django Social Auth exceptions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Handle specific social auth exceptions
        """
        if isinstance(exception, AuthAlreadyAssociated):
            logger.warning(f"AuthAlreadyAssociated exception for user attempting to login: {getattr(request, 'user', 'Unknown')}")
            
            # Set session flag to provide more context in the error page
            request.session['auth_already_associated'] = True
            
            # Redirect to custom error page
            return redirect(reverse('accounts:social_auth_error') + '?error_type=auth_already_associated')
        
        return None 