
from django.utils import timezone
from django.conf import settings
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class TokenExpiryMiddleware:
    """Middleware to check token expiry - 5 minutes as per requirements"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request has Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                # Check if token is expired (created more than TOKEN_EXPIRY_TIME ago)
                if timezone.now() - token.created > settings.TOKEN_EXPIRY_TIME:
                    token.delete()
                    logger.info(f"Expired token deleted for user: {token.user.email}")
                    # Token expired, authentication will fail in the view
            except Token.DoesNotExist:
                pass
        
        response = self.get_response(request)
        return response
