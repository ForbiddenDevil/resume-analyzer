from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Middleware to require login for all views except those specified in settings.EXEMPT_URLS
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_urls = getattr(settings, 'EXEMPT_URLS', [])
        
        # Check if the user is authenticated or if the URL is exempt
        if not request.user.is_authenticated and request.path not in exempt_urls:
            return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response