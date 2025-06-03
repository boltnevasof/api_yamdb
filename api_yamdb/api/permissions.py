from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
            or request.user.role in ('moderator', 'admin')
        )


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
