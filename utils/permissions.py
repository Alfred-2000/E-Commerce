from functools import wraps

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from accounts.utils import check_feature_permission


def required_superuser_access(view_func):
    """
    Decorator to check if the logged-in user has superuser privileges.

    This decorator intercepts the view function and checks if the user associated
    with the current request has superuser access by verifying their token.
    If the user is not a superuser, a `PermissionDenied` exception is raised.

    Usage:
        @required_superuser_access
        def some_view(self, request, *args, **kwargs):
            # View logic for superusers only
            pass

    Args:
        view_func (function): The view function to be decorated.

    Returns:
        function: A wrapped view function that first checks the user's superuser status
                  before executing the original view.
    """

    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        token = request.META.get("HTTP_AUTHORIZATION", None)
        if not check_feature_permission(token):
            raise PermissionDenied("You do not have permission to perform this action.")
        return view_func(self, request, *args, **kwargs)

    return _wrapped_view


class IsSuperUserPermission(permissions.BasePermission):
    """
    Custom permission to allow access only to superusers.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True


class IsObjectOwnerOrSuperUserPermission(permissions.BasePermission):
    """
    Custom permission to allow access to superusers or to the user who owns the object.
    """

    def has_object_permission(self, request, view, obj):
        obj_perm_status = False
        if request.user and request.user.is_superuser:
            obj_perm_status = True

        elif getattr(obj, "user_id", None) == request.user.user_id:
            obj_perm_status = True

        return obj_perm_status
