from django.contrib.auth import get_user_model
from django.db.models import Q, Subquery
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated

from dbschema.models import CoinWallet, Enrollment, Parent, ParentStudent, Student, Teacher, UserRole
from studiumx_main.authentication import AccessJWTAuthentication
from .permissions import SameSchoolOrAdmin, IsSchoolAdmin
from .serializers import (
    UserProfileSerializer,
    PublicUserCardSerializer,
    StudentAdminPatchSerializer,
)

User = get_user_model()


class UserProfileView(APIView):
    authentication_classes = (AccessJWTAuthentication,)
    permission_classes = (IsAuthenticated, SameSchoolOrAdmin)

    def get(self, request, user_id):
        user = User.objects.select_related("school").filter(id=user_id).first()

        if not user:
            raise NotFound("User not found.")

        self.check_object_permissions(request, user)

        roles = list(UserRole.objects.filter(user_id=user.id).values_list("role", flat=True))
        wallet = CoinWallet.objects.filter(user_id=user.id).only("balance").first()

        student = Student.objects.filter(user_id=user.id).first()
        teacher = Teacher.objects.select_related("user").filter(user_id=user.id).first()
        parent = Parent.objects.select_related("user").filter(user_id=user.id).first()

        if student:
            today = timezone.localdate()
            enrollment = (
                Enrollment.objects.select_related("class_group")
                .filter(student_id=student.user_id)
                .filter(Q(ends_on__isnull=True) | Q(ends_on__gte=today))
                .order_by("-starts_on")
                .first()
            )
            parent_link = (
                ParentStudent.objects.select_related("parent", "parent__user")
                .filter(student_id=student.user_id)
                .first()
            )
            setattr(student, "current_class", enrollment.class_group if enrollment else None)
            setattr(student, "parent", parent_link.parent if parent_link else None)
            setattr(student, "teacher", None)

        user._roles = roles or ([user.role] if getattr(user, "role", None) else [])
        user._wallet_balance = wallet.balance if wallet else 0
        user._student = student
        user._teacher = teacher
        user._parent = parent

        data = UserProfileSerializer(user).data
        print(data)
        return Response(data, status=status.HTTP_200_OK)


class UserSearchPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 50


class UserSearchView(ListAPIView):
    permission_classes = (IsSchoolAdmin,)
    serializer_class = PublicUserCardSerializer
    pagination_class = UserSearchPagination
    authentication_classes = (AccessJWTAuthentication,)

    def get_queryset(self):
        user = self.request.user
        school_id = getattr(user, "school_id", None)

        qs = User.objects.all().only("id", "email", "full_name", "role", "school_id")

        if school_id:
            qs = qs.filter(school_id=school_id)

        role = self.request.query_params.get("role")
        q = (self.request.query_params.get("q") or "").strip()

        if role:
            qs = qs.filter(
                Q(role=role) | Q(id__in=Subquery(UserRole.objects.filter(role=role).values("user_id")))
            )
        if q:
            qs = qs.filter(Q(email__icontains=q) | Q(full_name__icontains=q) | Q(phone__icontains=q))

        return qs.order_by("full_name", "email")


class StudentAdminUpdateView(APIView):
    permission_classes = (IsSchoolAdmin,)
    authentication_classes = (AccessJWTAuthentication,)

    def patch(self, request, user_id):
        student = User.objects.filter(id=user_id).first()
        print(student, user_id)
        if not student:
            raise NotFound("Student not found.")

        serializer = StudentAdminPatchSerializer(
            data=request.data,
            context={"request": request, "student": student},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        v = serializer.validated_data

        if "birth_date" in v:
            student.birth_date = v.get("birth_date")
            student.save(update_fields=["birth_date"])

        u = student
        u._student = student
        u._teacher = Teacher.objects.select_related("user").filter(user_id=u.id).first()
        u._parent = Parent.objects.select_related("user").filter(user_id=u.id).first()
        u._roles = list(UserRole.objects.filter(user_id=u.id).values_list("role", flat=True))
        wallet = CoinWallet.objects.filter(user_id=u.id).only("balance").first()
        u._wallet_balance = wallet.balance if wallet else 0

        return Response(UserProfileSerializer(u).data, status=status.HTTP_200_OK)
