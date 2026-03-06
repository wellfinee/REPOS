from rest_framework import serializers
from django.contrib.auth import get_user_model

from dbschema.models import ClassGroup, Parent, Student, Teacher, School

User = get_user_model()


class PublicUserCardSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = User
        fields = ("id", "full_name", "email")


class ClassMiniSerializer(serializers.ModelSerializer):
    title = serializers.CharField()

    class Meta:
        model = ClassGroup
        fields = ("id", "title")


class ParentMiniSerializer(serializers.ModelSerializer):
    user = PublicUserCardSerializer(read_only=True)

    class Meta:
        model = Parent
        fields = ("id", "user")


class TeacherMiniSerializer(serializers.ModelSerializer):
    user = PublicUserCardSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ("id", "user")


class StudentProfileSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    student_code = serializers.CharField(allow_null=True)
    birth_date = serializers.DateField(allow_null=True)
    current_class = ClassMiniSerializer(allow_null=True)
    parent = ParentMiniSerializer(allow_null=True)
    teacher = TeacherMiniSerializer(allow_null=True)


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ("user_id", "staff_code", "hired_on")


class ParentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ("user_id",)

class SchoolMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ("id", "name", "country_code", "city", "address")
class UserProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()
    profiles = serializers.SerializerMethodField()
    school = SchoolMiniSerializer(read_only=True)
    class Meta:
        model = User
        fields = ("id","full_name", "email", "roles", "wallet", "profiles", "school", "phone", "role")


    def get_roles(self, obj):
        roles = getattr(obj, "_roles", None)
        if roles is not None:
            return roles
        return [obj.role] if getattr(obj, "role", None) else []

    def get_wallet(self, obj):
        balance = getattr(obj, "_wallet_balance", 0)
        return {"balance": int(balance or 0)}

    def get_profiles(self, obj):
        student = getattr(obj, "_student", None)
        teacher = getattr(obj, "_teacher", None)
        parent = getattr(obj, "_parent", None)

        return {
            "student": None if not student else StudentProfileSerializer(student).data,
            "teacher": None if not teacher else TeacherProfileSerializer(teacher).data,
            "parent": None if not parent else ParentProfileSerializer(parent).data,
        }


class StudentAdminPatchSerializer(serializers.Serializer):
    parent_user_id = serializers.UUIDField(required=False, allow_null=True)
    teacher_user_id = serializers.UUIDField(required=False, allow_null=True)
    current_class_id = serializers.UUIDField(required=False, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        # Stub-compatible validation without extra DB chatter.
        return attrs
