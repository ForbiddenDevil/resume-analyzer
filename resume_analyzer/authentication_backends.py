# myapp/authentication_backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from teradataml import create_context

class CustomBackend(BaseBackend):
    """
    Custom authentication backend that authenticates users against an external API.
    """
    def authenticate(self, request, host=None, username=None, password=None):
        
        eng = create_context(host=host, username=username, password=password)

        if eng:
            print(eng)
            # Get or create the user in Django's database
            user, created = User.objects.get_or_create(username=username)
            if created:
                # Set additional user fields if needed
                user.password = make_password(password)  # Optional: store hashed password
                user.save()
            return user  # Authentication successful
        return None  # Authentication failed

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
