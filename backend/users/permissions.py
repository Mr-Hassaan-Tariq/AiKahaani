"""
Permission classes for the users app.
"""

import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class IsAdminPermission(BasePermission):
    """
    Permission class that only allows access to users with admin role.

    This permission checks if the current authenticated user has the admin role
    assigned to them. Users can have multiple roles, so this checks if the
    admin role is among their assigned roles.

    Usage:
        permission_classes = [IsAuthenticated, IsAdminPermission]
    """

    message = "You must have admin role to access this resource."

    def has_permission(self, request, view):
        """
        Check if the user has admin role.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if user has admin role, False otherwise
        """
        # First check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            # Check if user has admin role or is superuser
            if request.user.is_admin() or request.user.is_superuser:
                return True
            else:
                return False
        except Exception:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check (same as has_permission for this use case).

        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The object being accessed

        Returns:
            bool: True if user has admin role, False otherwise
        """
        return self.has_permission(request, view)
