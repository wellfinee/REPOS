from __future__ import annotations

import uuid
from django.db import models
from django.utils import timezone

from . import choices

class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    country_code = models.TextField()
    city = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'schools'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class AcademicYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    name = models.TextField()
    starts_on = models.DateField()
    ends_on = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'academic_years'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class Term(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.ForeignKey('AcademicYear', db_column='academic_year_id', on_delete=models.PROTECT, related_name='+')
    name = models.TextField()
    starts_on = models.DateField()
    ends_on = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'terms'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class GradeLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    grade = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'grade_levels'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class ClassGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    academic_year = models.ForeignKey('AcademicYear', db_column='academic_year_id', on_delete=models.PROTECT, related_name='+')
    grade_level = models.ForeignKey('GradeLevel', db_column='grade_level_id', on_delete=models.PROTECT, related_name='+')
    name = models.TextField()
    homeroom_teacher_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'class_groups'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    email = models.EmailField(max_length=254, null=True, blank=True, unique=True)
    phone = models.TextField(null=True, blank=True, unique=True)
    password_hash = models.TextField()
    password = models.TextField()
    role = models.TextField(null=True, blank=True)
    full_name = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'users'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class UserRole(models.Model):
    user = models.ForeignKey('User', db_column='user_id', on_delete=models.CASCADE, related_name='+')
    role = models.CharField(max_length=8, choices=choices.UserRole.choices)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'user_roles'
        unique_together = (('user', 'role'),)

    def __str__(self):
        return str(getattr(self, 'id', ''))

class Teacher(models.Model):
    user = models.OneToOneField(
        'User',
        db_column='user_id',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='+',
    )
    staff_code = models.TextField(null=True, blank=True)
    hired_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'teachers'

    def __str__(self):
        return str(getattr(self, 'user_id', ''))
class Student(models.Model):
    user = models.OneToOneField(
        "User",
        db_column="user_id",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="+",
    )
    student_code = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "students"

class Parent(models.Model):
    user = models.OneToOneField(
        'User',
        db_column='user_id',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='+',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'parents'

    def __str__(self):
        return str(getattr(self, 'user_id', ''))

class ParentStudent(models.Model):
    parent = models.ForeignKey('Parent', db_column='parent_id', on_delete=models.CASCADE, related_name='+')
    student = models.ForeignKey('Student', db_column='student_id', on_delete=models.CASCADE, related_name='+')
    relation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'parent_students'
        unique_together = (('parent', 'student'),)

    def __str__(self):
        return str(getattr(self, 'id', ''))


class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Student', db_column='student_id', on_delete=models.CASCADE, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'enrollments'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    name = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'subjects'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class TeachingAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    academic_year = models.ForeignKey('AcademicYear', db_column='academic_year_id', on_delete=models.PROTECT, related_name='+')
    term = models.ForeignKey('Term', db_column='term_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    subject = models.ForeignKey('Subject', db_column='subject_id', on_delete=models.PROTECT, related_name='+')
    teacher = models.ForeignKey('Teacher', db_column='teacher_id', on_delete=models.PROTECT, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'teaching_assignments'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class TimetablePeriod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    period_no = models.IntegerField()
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'timetable_periods'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class TimetableEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    academic_year = models.ForeignKey('AcademicYear', db_column='academic_year_id', on_delete=models.PROTECT, related_name='+')
    term = models.ForeignKey('Term', db_column='term_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    weekday = models.CharField(max_length=3, choices=choices.Weekday.choices)
    period = models.ForeignKey('TimetablePeriod', db_column='period_id', on_delete=models.PROTECT, related_name='+')
    subject = models.ForeignKey('Subject', db_column='subject_id', on_delete=models.PROTECT, related_name='+')
    teacher = models.ForeignKey('Teacher', db_column='teacher_id', on_delete=models.PROTECT, related_name='+')
    room = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'timetable_entries'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    subject = models.ForeignKey('Subject', db_column='subject_id', on_delete=models.PROTECT, related_name='+')
    teacher = models.ForeignKey('Teacher', db_column='teacher_id', on_delete=models.PROTECT, related_name='+')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    room = models.TextField(null=True, blank=True)
    topic = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'lessons'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class FileAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_user = models.ForeignKey('User', db_column='owner_user_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    url = models.TextField()
    filename = models.TextField(null=True, blank=True)
    mime_type = models.TextField(null=True, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    sha256 = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'file_assets'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class Homework(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    subject = models.ForeignKey('Subject', db_column='subject_id', on_delete=models.PROTECT, related_name='+')
    teacher = models.ForeignKey('Teacher', db_column='teacher_id', on_delete=models.PROTECT, related_name='+')
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    assigned_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'homework'

    def __str__(self):
        return str(getattr(self, 'title', getattr(self,'id','')))


class HomeworkAttachment(models.Model):
    homework = models.ForeignKey('Homework', db_column='homework_id', on_delete=models.CASCADE, related_name='+')
    file = models.ForeignKey('FileAsset', db_column='file_id', on_delete=models.PROTECT, related_name='+')

    class Meta:
        managed = False
        db_table = 'homework_attachments'
        unique_together = (('homework', 'file'),)

    def __str__(self):
        return str(getattr(self, 'id', ''))


class HomeworkSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    homework = models.ForeignKey('Homework', db_column='homework_id', on_delete=models.CASCADE, related_name='+')
    student = models.ForeignKey('Student', db_column='student_id', on_delete=models.CASCADE, related_name='+')
    status = models.CharField(max_length=9, choices=choices.SubmissionStatus.choices)
    text_answer = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey('Teacher', db_column='graded_by', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    teacher_feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'homework_submissions'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class HomeworkSubmissionFile(models.Model):
    submission = models.ForeignKey('HomeworkSubmission', db_column='submission_id', on_delete=models.CASCADE, related_name='+')
    file = models.ForeignKey('FileAsset', db_column='file_id', on_delete=models.PROTECT, related_name='+')

    class Meta:
        managed = False
        db_table = 'homework_submission_files'
        unique_together = (('submission', 'file'),)

    def __str__(self):
        return str(getattr(self, 'id', ''))


class HomeworkComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('HomeworkSubmission', db_column='submission_id', on_delete=models.CASCADE, related_name='+')
    author_user = models.ForeignKey('User', db_column='author_user_id', on_delete=models.CASCADE, related_name='+')
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'homework_comments'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    subject = models.ForeignKey('Subject', db_column='subject_id', on_delete=models.PROTECT, related_name='+')
    teacher = models.ForeignKey('Teacher', db_column='teacher_id', on_delete=models.PROTECT, related_name='+')
    term = models.ForeignKey('Term', db_column='term_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    type_field = models.CharField(max_length=7, choices=choices.AssessmentType.choices)
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'assessments'

    def __str__(self):
        return str(getattr(self, 'title', getattr(self,'id','')))


class AssessmentResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey('Assessment', db_column='assessment_id', on_delete=models.CASCADE, related_name='+')
    student = models.ForeignKey('Student', db_column='student_id', on_delete=models.CASCADE, related_name='+')
    score = models.DecimalField(max_digits=6, decimal_places=2)
    graded_at = models.DateTimeField(default=timezone.now)
    graded_by = models.ForeignKey('Teacher', db_column='graded_by', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'assessment_results'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class GradebookEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, related_name='+')
    class_group = models.ForeignKey('ClassGroup', db_column='class_group_id', on_delete=models.PROTECT, related_name='+')
    subject = models.ForeignKey('Subject', db_column='subject_id', on_delete=models.PROTECT, related_name='+')
    student = models.ForeignKey('Student', db_column='student_id', on_delete=models.CASCADE, related_name='+')
    teacher = models.ForeignKey('Teacher', db_column='teacher_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    source_type = models.TextField()
    source_id = models.UUIDField()
    score = models.DecimalField(max_digits=6, decimal_places=2)
    max_score = models.DecimalField(max_digits=6, decimal_places=2)
    occurred_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'gradebook_entries'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class CoinWallet(models.Model):
    user = models.OneToOneField(
        'User',
        db_column='user_id',
        on_delete=models.CASCADE,
        primary_key=True
    )
    balance = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'coin_wallets'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class CoinTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_user = models.ForeignKey('CoinWallet', db_column='wallet_user_id', on_delete=models.CASCADE, related_name='+')
    type_field = models.CharField(max_length=6, choices=choices.CoinTxnType.choices)
    delta = models.BigIntegerField()
    reason = models.TextField()
    reference_id = models.UUIDField(null=True, blank=True)
    created_by = models.ForeignKey('User', db_column='created_by', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'coin_transactions'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class Achievement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    code = models.TextField()
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    icon_file = models.ForeignKey('FileAsset', db_column='icon_file_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'achievements'

    def __str__(self):
        return str(getattr(self, 'title', getattr(self,'id','')))

class UserAchievement(models.Model):
    id = models.UUIDField(primary_key=True)

    user = models.ForeignKey("User", db_column="user_id", on_delete=models.CASCADE, related_name="+")
    achievement = models.ForeignKey("Achievement", db_column="achievement_id", on_delete=models.PROTECT, related_name="+")
    awarded_at = models.DateTimeField(default=timezone.now)

    awarded_by = models.ForeignKey(
        "User",
        db_column="awarded_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    meta = models.JSONField()

    class Meta:
        managed = False
        db_table = "user_achievements"
        # unique_together можно оставить, но лучше уже constraint в БД
        unique_together = (("user", "achievement"),)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    type_field = models.CharField(max_length=8, choices=choices.ProductType.choices)
    sku = models.TextField(null=True, blank=True)
    title = models.TextField()
    description = models.TextField(null=True, blank=True)
    price_coins = models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    digital_file = models.ForeignKey('FileAsset', db_column='digital_file_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'products'

    def __str__(self):
        return str(getattr(self, 'title', getattr(self,'id','')))


class ProductInventory(models.Model):
    product = models.ForeignKey('Product', db_column='product_id', on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'product_inventory'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer_user = models.ForeignKey('User', db_column='buyer_user_id', on_delete=models.PROTECT, related_name='+')
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    status = models.CharField(max_length=10, choices=choices.OrderStatus.choices)
    total_price_coins = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'orders'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey('Order', db_column='order_id', on_delete=models.CASCADE, related_name='+')
    product = models.ForeignKey('Product', db_column='product_id', on_delete=models.PROTECT, related_name='+')
    qty = models.IntegerField(default=1)
    unit_price_coins = models.BigIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'order_items'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class OrderDelivery(models.Model):
    order = models.ForeignKey('Order', db_column='order_id', on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    recipient_name = models.TextField()
    phone = models.TextField(null=True, blank=True)
    address = models.TextField()
    notes = models.TextField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'order_deliveries'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class DigitalEntitlement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', db_column='user_id', on_delete=models.CASCADE, related_name='+')
    product = models.ForeignKey('Product', db_column='product_id', on_delete=models.PROTECT, related_name='+')
    order = models.ForeignKey('Order', db_column='order_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    granted_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField()

    class Meta:
        managed = False
        db_table = 'digital_entitlements'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class RouletteConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', db_column='school_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    name = models.TextField()
    spin_cost_coins = models.BigIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'roulette_configs'

    def __str__(self):
        return str(getattr(self, 'name', getattr(self,'id','')))


class RouletteReward(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey('RouletteConfig', db_column='config_id', on_delete=models.CASCADE, related_name='+')
    weight = models.IntegerField(default=1)
    outcome = models.CharField(max_length=11, choices=choices.RouletteOutcome.choices)
    coins_amount = models.BigIntegerField(null=True, blank=True)
    product = models.ForeignKey('Product', db_column='product_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    achievement = models.ForeignKey('Achievement', db_column='achievement_id', on_delete=models.PROTECT, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'roulette_rewards'

    def __str__(self):
        return str(getattr(self, 'id', ''))


class RouletteSpin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey('RouletteConfig', db_column='config_id', on_delete=models.PROTECT, related_name='+')
    user = models.ForeignKey('User', db_column='user_id', on_delete=models.PROTECT, related_name='+')
    cost_coins = models.BigIntegerField()
    outcome = models.CharField(max_length=11, choices=choices.RouletteOutcome.choices)
    reward = models.ForeignKey('RouletteReward', db_column='reward_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    coins_awarded = models.BigIntegerField(null=True, blank=True)
    product_awarded = models.ForeignKey('Product', db_column='product_awarded_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    achievement_awarded = models.ForeignKey('Achievement', db_column='achievement_awarded_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'roulette_spins'

    def __str__(self):
        return str(getattr(self, 'id', ''))

