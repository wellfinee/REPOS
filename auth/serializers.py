# apps/auth/serializers.py
from rest_framework import serializers
from dbschema.models import (
    User, School, UserRole,
    CoinWallet,
    Achievement, UserAchievement,
    FileAsset,
    Student, Teacher, Parent,
    Enrollment, ClassGroup, GradeLevel, AcademicYear,
)

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "country_code", "city", "address"]


class FileAssetMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAsset
        fields = ["id", "url", "filename", "mime_type", "size_bytes"]


class AchievementSerializer(serializers.ModelSerializer):
    icon_file = FileAssetMiniSerializer(read_only=True)

    class Meta:
        model = Achievement
        fields = ["id", "code", "title", "description", "icon_file"]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ["achievement", "awarded_at", "meta"]


class EnrollmentMiniSerializer(serializers.Serializer):
    class_group_id = serializers.UUIDField()
    class_group_name = serializers.CharField()
    grade = serializers.IntegerField()
    academic_year_name = serializers.CharField()


class MeSerializer(serializers.Serializer):
    """
    Мы не используем ModelSerializer на User напрямую, потому что:
    - reverse relations отключены (related_name='+')
    - данные собираем вручную в view
    """

    id = serializers.UUIDField()
    full_name = serializers.CharField()
    email = serializers.EmailField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()

    school = SchoolSerializer(allow_null=True)
    roles = serializers.ListField(child=serializers.CharField())
    wallet = serializers.DictField()
    achievements = UserAchievementSerializer(many=True)

    profiles = serializers.DictField()
    current_enrollment = serializers.DictField(allow_null=True)