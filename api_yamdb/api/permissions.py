from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Администратор или только чтение."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class AdminOnly(permissions.BasePermission):
    """
    Только пользователи с правами администратора (is_staff)
    или ролью 'admin' имеют разрешение на доступ.
    """

    def has_permission(self, request, view):
        """Проверяет разрешение доступа на уровне представления."""
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.role == 'admin'
            )
        )
