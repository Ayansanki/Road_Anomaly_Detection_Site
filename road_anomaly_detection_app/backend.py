from django.contrib.auth.backends import BaseBackend
from .models import User
from django.core.exceptions import ObjectDoesNotExist

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email.lower())
            
            if user.check_password(password) and user.is_active:
                return user

            return None
        
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        # try:
        #     return User.objects.get(pk=user_id)
        # except User.DoesNotExist:
        #     return None
        if user_id is None:
            return None
        try:
            # Assume pk is int (default AutoField); adjust if custom PK
            user = User.objects.get(pk=int(user_id))  # Cast to int for safety
            return user if user.is_active else None  # Only return active users
        except (User.DoesNotExist, ValueError, TypeError):
            return None