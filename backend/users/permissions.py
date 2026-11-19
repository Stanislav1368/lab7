from rest_framework.permissions import BasePermission

from .models import User


def is_admin_user(user) -> bool:
    """Единая проверка «администратор» для прав и бизнес-логики."""
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or getattr(user, "role", None) == User.Role.ADMIN
        )
    )


class IsAdminRole(BasePermission):
    """Доступ только администратору (роль admin / is_staff / is_superuser)."""

    def has_permission(self, request, view):
        return is_admin_user(request.user)


class IsOwnerOrAdmin(BasePermission):
    """Объект доступен его владельцу (obj.user) или администратору."""

    def has_object_permission(self, request, view, obj):
        if is_admin_user(request.user):
            return True
        return getattr(obj, "user", None) == request.user
