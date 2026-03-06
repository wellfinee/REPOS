# studiumx_main/auth/views.py
from __future__ import annotations

import uuid
from typing import Optional

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authcore.jwt import decode_token, make_access_token, make_refresh_token
from authcore.models import RefreshToken
from dbschema.models import (
    CoinWallet,
    Enrollment,
    Parent,
    Student,
    Teacher,
    User,
    UserAchievement,
    UserRole,
)
from studiumx_main.authentication import AccessJWTAuthentication

REFRESH_COOKIE_NAME = "refresh_token"


# -----------------------
# Cookie helpers
# -----------------------
def _cookie_cfg():
    secure = bool(getattr(settings, "AUTH_COOKIE_SECURE", False))
    samesite = getattr(settings, "AUTH_COOKIE_SAMESITE", "Lax")
    domain = getattr(settings, "AUTH_COOKIE_DOMAIN", None)

    # SameSite=None требует Secure=True (иначе браузер режет cookie)
    if str(samesite).lower() == "none" and not secure:
        secure = True

    return secure, samesite, domain


def _set_refresh_cookie(resp: Response, refresh_token: str, *, max_age: int | None) -> None:
    secure, samesite, domain = _cookie_cfg()
    resp.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        domain=domain,
        path="/",
        max_age=max_age,  # None => session-cookie
    )


def _clear_refresh_cookie(resp: Response) -> None:
    # ВАЖНО: удаляем с теми же атрибутами домена/пути, иначе может "не удалиться"
    secure, samesite, domain = _cookie_cfg()
    resp.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/",
        domain=domain,
    )
    # delete_cookie сам выставляет Max-Age=0, но домен/путь важны


# -----------------------
# Token issuing / rotation
# -----------------------
class IssueTokensMixin:
    @staticmethod
    @transaction.atomic
    def _issue_tokens_for_user(
        user: User,
        *,
        refresh_ttl_seconds: int,
        is_persistent: bool,
        rotate_from_jti: Optional[uuid.UUID] = None,
    ) -> tuple[str, str, uuid.UUID, timezone.datetime]:
        """
        Returns:
          access, refresh, new_jti, refresh_exp_dt

        - creates RefreshToken row
        - optionally rotates old refresh (revokes + links replaced_by_jti)
        """
        access = make_access_token(str(user.id))

        # make_refresh_token now supports ttl_seconds in your jwt.py
        refresh, new_jti, exp_dt = make_refresh_token(
            str(user.id),
            ttl_seconds=int(refresh_ttl_seconds),
        )

        RefreshToken.objects.create(
            user_id=user.id,
            jti=new_jti,
            expires_at=exp_dt,
            is_persistent=is_persistent,
        )

        if rotate_from_jti:
            RefreshToken.objects.filter(jti=rotate_from_jti, revoked_at__isnull=True).update(
                revoked_at=timezone.now(),
                replaced_by_jti=new_jti,
            )

        return access, refresh, new_jti, exp_dt


def _refresh_ttl_for_mode(is_persistent: bool) -> int:
    return int(
        settings.AUTH_REFRESH_TTL_REMEMBER_SECONDS
        if is_persistent
        else settings.AUTH_REFRESH_TTL_SESSION_SECONDS
    )


# -----------------------
# Auth endpoints
# -----------------------
class LoginView(APIView, IssueTokensMixin):
    permission_classes = (AllowAny,)

    def post(self, request):
        identifier = (request.data.get("identifier") or "").strip()
        password = request.data.get("password") or ""
        remember_me = bool(request.data.get("remember_me"))

        if not identifier or not password:
            return Response({"success": False, "errors": {"detail": "identifier and password required"}}, status=400)

        qs = User.objects.filter(deleted_at__isnull=True, is_active=True)

        if "@" in identifier:
            user = qs.filter(email__iexact=identifier).first()
        else:
            user = qs.filter(phone=identifier).first()

        # одинаковый ответ для user not found / wrong password
        if not user or not user.password or not check_password(password, user.password):
            return Response({"success": False, "errors": {"detail": "Invalid credentials"}}, status=400)

        refresh_ttl = _refresh_ttl_for_mode(remember_me)

        access, refresh, _, _ = self._issue_tokens_for_user(
            user,
            refresh_ttl_seconds=refresh_ttl,
            is_persistent=remember_me,
        )

        resp = Response({"success": True, "access": access}, status=200)
        resp["Cache-Control"] = "no-store"

        _set_refresh_cookie(resp, refresh, max_age=(refresh_ttl if remember_me else None))
        return resp


class RefreshView(APIView, IssueTokensMixin):
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if not token:
            return Response({"success": False, "errors": {"detail": "No refresh cookie"}}, status=401)

        try:
            payload = decode_token(token)
        except Exception:
            return Response({"success": False, "errors": {"detail": "Invalid refresh token"}}, status=401)

        if payload.get("typ") != "refresh":
            return Response({"success": False, "errors": {"detail": "Wrong token type"}}, status=401)

        user_id = payload.get("user_id") or payload.get("sub")
        jti_str = payload.get("jti")
        if not user_id or not jti_str:
            return Response({"success": False, "errors": {"detail": "Invalid refresh token"}}, status=401)

        try:
            old_jti = uuid.UUID(str(jti_str))
        except ValueError:
            return Response({"success": False, "errors": {"detail": "Invalid refresh token"}}, status=401)

        rt = RefreshToken.objects.filter(jti=old_jti).first()
        if not rt:
            return Response({"success": False, "errors": {"detail": "Refresh revoked/expired"}}, status=401)

        if rt.revoked_at is not None or rt.expires_at <= timezone.now():
            return Response({"success": False, "errors": {"detail": "Refresh revoked/expired"}}, status=401)

        if str(rt.user_id) != str(user_id):
            return Response({"success": False, "errors": {"detail": "Refresh token subject mismatch"}}, status=401)

        user = User.objects.select_related("school").filter(id=user_id, is_active=True, deleted_at__isnull=True).first()
        if not user:
            return Response({"success": False, "errors": {"detail": "User not found"}}, status=401)

        is_persistent = bool(getattr(rt, "is_persistent", False))
        refresh_ttl = _refresh_ttl_for_mode(is_persistent)

        new_access, new_refresh, _, _ = self._issue_tokens_for_user(
            user,
            refresh_ttl_seconds=refresh_ttl,
            is_persistent=is_persistent,
            rotate_from_jti=old_jti,
        )

        resp = Response({"success": True, "access": new_access}, status=200)
        resp["Cache-Control"] = "no-store"

        _set_refresh_cookie(resp, new_refresh, max_age=(refresh_ttl if is_persistent else None))
        return resp


class LogoutView(APIView):
    """
    Revoke refresh token in DB (if possible) and clear cookie on client.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        token = request.COOKIES.get(REFRESH_COOKIE_NAME)

        if token:
            try:
                payload = decode_token(token)
                if payload.get("typ") == "refresh" and payload.get("jti"):
                    jti = uuid.UUID(str(payload["jti"]))
                    RefreshToken.objects.filter(jti=jti, revoked_at__isnull=True).update(
                        revoked_at=timezone.now()
                    )
            except Exception:
                pass

        resp = Response({"success": True}, status=200)
        _clear_refresh_cookie(resp)
        return resp


# -----------------------
# /me endpoint (оставил твою логику почти без изменений)
# -----------------------
class MeView(APIView):
    authentication_classes = (AccessJWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        roles = list(UserRole.objects.filter(user_id=user.id).values_list("role", flat=True))
        if not roles and getattr(user, "role", None):
            roles = [user.role]

        wallet = CoinWallet.objects.only("balance").filter(user_id=user.id).first()
        wallet_payload = {"balance": int(wallet.balance) if wallet else 0}

        student = Student.objects.only("user_id", "student_code", "birth_date").filter(user_id=user.id).first()
        teacher = Teacher.objects.only("user_id", "staff_code", "hired_on").filter(user_id=user.id).first()
        parent = Parent.objects.only("user_id").filter(user_id=user.id).first()

        profiles = {
            "student": None if not student else {
                "user_id": str(student.pk),
                "student_code": student.student_code,
                "birth_date": student.birth_date,
            },
            "teacher": None if not teacher else {
                "user_id": str(teacher.pk),
                "staff_code": teacher.staff_code,
                "hired_on": teacher.hired_on,
            },
            "parent": None if not parent else {
                "user_id": str(parent.pk),
            },
        }

        current_enrollment = None
        if student:
            today = timezone.localdate()
            enr = (
                Enrollment.objects
                .filter(student_id=student.pk)
                .filter(Q(ends_on__isnull=True) | Q(ends_on__gte=today))
                .order_by("-starts_on")
                .select_related("class_group", "class_group__grade_level", "class_group__academic_year")
                .first()
            )
            if enr:
                cg = enr.class_group
                current_enrollment = {
                    "class_group_id": str(cg.id),
                    "class_group_name": cg.name,
                    "grade": cg.grade_level.grade,
                    "academic_year_name": cg.academic_year.name,
                }

        ua_qs = (
            UserAchievement.objects
            .filter(user_id=user.id)
            .select_related("achievement", "achievement__icon_file")
            .order_by("-awarded_at")
        )

        achievements_payload = []
        for ua in ua_qs:
            a = ua.achievement
            icon = a.icon_file
            achievements_payload.append({
                "awarded_at": ua.awarded_at,
                "meta": ua.meta,
                "achievement": {
                    "id": str(a.id),
                    "code": a.code,
                    "title": a.title,
                    "description": a.description,
                    "icon_file": None if not icon else {
                        "id": str(icon.id),
                        "url": icon.url,
                        "filename": icon.filename,
                        "mime_type": icon.mime_type,
                        "size_bytes": icon.size_bytes,
                    },
                },
            })

        return Response({
            "success": True,
            "user": {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active,
                "school": None if not user.school_id else {
                    "id": str(user.school_id),
                    "name": user.school.name,
                    "country_code": user.school.country_code,
                    "city": user.school.city,
                    "address": user.school.address,
                },
                "roles": roles,
                "wallet": wallet_payload,
                "profiles": profiles,
                "current_enrollment": current_enrollment,
                "achievements": achievements_payload,
            }
        }, status=200)