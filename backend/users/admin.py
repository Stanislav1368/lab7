from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Стандартная админка пользователя + поле role."""

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Роль в магазине", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Роль в магазине", {"fields": ("role",)}),
    )
    list_display = ("id", "username", "email", "role", "is_staff", "is_active")
    list_filter = DjangoUserAdmin.list_filter + ("role",)
