from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение на редактирование и удаление только для:
    - автора,
    - модератора,
    - администратора.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS  # GET, HEAD, OPTIONS
            or obj.author == request.user               # автор
            or getattr(request.user, 'role', '') in ['moderator', 'admin']  # модератор или админ
            or request.user.is_staff                    # для суперюзера
        )
