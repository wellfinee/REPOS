import uuid
import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone

def _now():
    return datetime.now(timezone.utc)

def make_access_token(user_id: str) -> str:
    now = _now()
    exp = now + settings.JWT_ACCESS_TTL
    payload = {
        "typ": "access",
        "iss": settings.JWT_ISSUER,
        "sub": str(user_id),
        "user_id": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def make_refresh_token(
    user_id: str,
    jti: uuid.UUID | None = None,
    ttl_seconds: int | None = None,   # ✅ добавили
) -> tuple[str, uuid.UUID, datetime]:
    now = _now()

    # ✅ если ttl_seconds передан — используем его, иначе дефолт settings.JWT_REFRESH_TTL
    if ttl_seconds is None:
        exp = now + settings.JWT_REFRESH_TTL
    else:
        exp = now + timedelta(seconds=int(ttl_seconds))

    jti = jti or uuid.uuid4()

    payload = {
        "typ": "refresh",
        "iss": settings.JWT_ISSUER,
        "sub": str(user_id),
        "user_id": str(user_id),
        "jti": str(jti),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, exp


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_aud": False},
        issuer=settings.JWT_ISSUER,
    )