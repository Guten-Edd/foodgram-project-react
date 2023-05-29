from rest_framework.permissions import SAFE_METHODS, BasePermission
from users.models import USERS_ROLE


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.role == USERS_ROLE.ADMIN)
