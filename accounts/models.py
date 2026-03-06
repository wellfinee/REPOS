import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("Нужен email или phone")

        if email:
            email = self.normalize_email(email)

        user = self.model(email=email, phone=phone, **extra_fields)

        if password:
            user.set_password(password)  # ✅ пишет Django-хэш в поле password
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SCHOOL_ADMIN = "SCHOOL_ADMIN", "School Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        PARENT = "PARENT", "Parent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ВАЖНО: 'School' должен быть реальной моделью. Путь поправь под свой проект.
    school = models.ForeignKey(
        "schools.School",
        db_column="school_id",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
    )

    email = models.EmailField(max_length=254, null=True, blank=True, unique=True)
    phone = models.TextField(null=True, blank=True, unique=True)

    full_name = models.TextField(db_column="full_name", blank=True, default="")

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)        # ✅ нужно для admin
    # is_superuser уже есть из PermissionsMixin и маппится в колонку is_superuser

    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)  # оставляем твоё поле
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    # Логин по email (можно поменять на phone, но тогда нужно больше логики)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.phone or str(self.id)