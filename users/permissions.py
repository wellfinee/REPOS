# apps/users/permissions.py
from __future__ import annotations

from rest_framework.permissions import BasePermission

from dbschema.models import UserRole  # если у тебя это именно так


def _is_true(obj, attr: str) -> bool:
    return bool(getattr(obj, attr, False))


def _user_roles(user) -> set[str]:
    """
    Возвращает множество ролей пользователя.
    Поддерживает:
      - user.role
      - user.roles (list/tuple/set)
      - таблицу UserRole (many-to-many)
    """
    roles: set[str] = set()

    role = getattr(user, "role", None)
    if role:
        roles.add(str(role))

    many = getattr(user, "roles", None)
    if isinstance(many, (list, tuple, set)):
        roles |= {str(r) for r in many if r}

    # Если есть таблица UserRole — достанем оттуда (быстро и надёжно)
    # Важно: не делаем запросы для анонимного
    user_id = getattr(user, "id", None)
    if user_id:
        try:
            db_roles = UserRole.objects.filter(user_id=user_id).values_list("role", flat=True)
            roles |= {str(r) for r in db_roles if r}
        except Exception:
            # если в каком-то окружении модели нет/не подключена — не валимся
            pass

    return roles


def _is_admin_like(user) -> bool:
    # если вдруг у тебя есть is_superuser/is_staff — учитываем, но безопасно
    if _is_true(user, "is_superuser") or _is_true(user, "is_staff"):
        return True

    roles = _user_roles(user)
    return "SCHOOL_ADMIN" in roles or "ADMIN" in roles


class IsSchoolAdmin(BasePermission):
    message = "Only SCHOOL_ADMIN can perform this action."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return "SCHOOL_ADMIN" in _user_roles(user) or _is_true(user, "is_superuser")


class SameSchoolOrAdmin(BasePermission):
    """
    Просмотр профилей:
      - админы (SCHOOL_ADMIN/ADMIN/is_superuser) могут видеть всех
      - остальные — только пользователей своей школы
    """

    message = "Not allowed to view this profile."

    def has_permission(self, request, view):
        return bool(getattr(request, "user", None) and getattr(request.user, "is_authenticated", False))

    def has_object_permission(self, request, view, obj_user):
        user = request.user

        if _is_admin_like(user):
            return True

        return getattr(user, "school_id", None) == getattr(obj_user, "school_id", None)