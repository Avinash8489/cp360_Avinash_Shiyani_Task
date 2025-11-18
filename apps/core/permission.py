from rest_framework import permissions
from apps.user.constants import UserRoles


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == UserRoles.ADMIN and request.user.is_staff and request.user.is_superuser


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == UserRoles.STAFF or request.user.is_staff


class IsAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == UserRoles.END_USER
