# accounts/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.throttling import ScopedRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer
from .throttles import LoginIdentifierThrottle

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle, LoginIdentifierThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        remember = serializer.validated_data["remember"]

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Если remember=False, делаем refresh короче логически:
        # (SimpleJWT lifetimes глобальны, но можно хранить refresh в cookie с max-age меньше)
        data = {
            "access": str(access),
            "refresh": str(refresh),  # можно НЕ отдавать в body, а класть только в HttpOnly cookie
            "user": {
                "id": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "role": getattr(user, "role", None),
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
        }

        resp = Response(data, status=status.HTTP_200_OK)

        # Максимально безопасно: refresh хранить в HttpOnly cookie (опционально)
        # В dev (http) Secure=False. В prod ставь Secure=True и SameSite='Strict'/'Lax' по сценарию.
        # Если хочешь — включишь это и НЕ будешь возвращать refresh в JSON.
        """
        cookie_max_age = 60 * 60 * 24 * (30 if remember else 1)  # пример: 30d или 1d
        resp.set_cookie(
            "refresh_token",
            str(refresh),
            max_age=cookie_max_age,
            httponly=True,
            secure=False,      # PROD: True
            samesite="Lax",    # PROD: Lax/Strict
        )
        """

        return resp