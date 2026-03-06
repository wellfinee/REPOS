from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    ordering = ("-created_at",)

    list_display = ("id", "email", "phone", "full_name", "role", "school", "is_active", "is_staff", "is_superuser")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")

    fieldsets = (
        (None, {"fields": ("email", "phone", "password")}),
        ("Profile", {"fields": ("full_name", "role", "school")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined", "created_at", "updated_at", "deleted_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "full_name", "role", "school", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    search_fields = ("email", "phone", "full_name")