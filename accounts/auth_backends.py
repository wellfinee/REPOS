# accounts/auth_backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(BaseBackend):
    """
    authenticate(identifier=..., password=...)
    identifier может быть email или phone.
    """
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        if not identifier or not password:
            return None

        # Быстро: один запрос, без лишнего
        qs = User.objects.only("id", "email", "phone", "password", "is_active")
        if "@" in identifier:
            user = qs.filter(email__iexact=identifier).first()
        else:
            user = qs.filter(phone=identifier).first()

        if not user:
            return None

        # check_password делает безопасное сравнение и защищает от timing attacks
        if user.check_password(password) and user.is_active:
            return user

        return None

    def get_user(self, user_id):
        return User.objects.filter(pk=user_id).first()