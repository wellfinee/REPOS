# apps/authentication.py
from __future__ import annotations

import uuid

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from dbschema.models import User


class AccessJWTAuthentication(BaseAuthentication):
    """
    Authorization: Bearer <access_token>

    Ожидаемые claims (как в твоём make_access_token):
      typ=access
      iss=settings.JWT_ISSUER
      sub/user_id = uuid
      exp/iat
    """

    keyword = "Bearer"

    def authenticate(self, request):
        header = request.headers.get("Authorization") or ""
        if not header:
            return None

        parts = header.split(" ", 1)
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1].strip()
        if not token:
            return None

        try:
            print(token)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_aud": False},
                issuer=settings.JWT_ISSUER,  # ✅ так же, как в decode_token()
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Access token expired")
        except jwt.InvalidIssuerError:
            raise AuthenticationFailed("Invalid token issuer")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid access token")

        # ✅ тип токена
        if payload.get("typ") != "access":
            raise AuthenticationFailed("Wrong token type")

        raw_user_id = payload.get("user_id") or payload.get("sub")
        if not raw_user_id:
            raise AuthenticationFailed("Token missing user_id/sub")

        # ✅ UUID нормализация
        try:
            user_uuid = uuid.UUID(str(raw_user_id))
        except ValueError:
            raise AuthenticationFailed("Invalid user_id in token")

        user = (
            User.objects
            .filter(id=user_uuid, is_active=True, deleted_at__isnull=True)
            .select_related("school")
            .first()
        )
        if not user:
            raise AuthenticationFailed("User not found")

        return (user, None)