from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Изменение только для автора или админа."""

    def has_object_permission(self, request, view, obj):
        if (obj.author == request.user or request.user.is_staff):
            return True
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Безопасные методы для всех, а изменение только для автора."""

    message = "Отсутствует доступ на изменение и удаление чужого контента"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Безопасные методы для всех, а изменение только для админ."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)
