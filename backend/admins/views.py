from django.contrib.auth import get_user_model
from drf_spectacular.openapi import OpenApiExample, OpenApiParameter
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from admins.serializers import (
    AdminUserDetailSerializer,
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
)
from users.models import Role
from users.permissions import IsAdminPermission

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=["Admin"],
        summary="List Users",
        description="Retrieve a paginated list of users with filtering and search capabilities.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of items per page",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search by name, email, or username",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by status (active/inactive)",
            ),
            OpenApiParameter(
                name="role",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by role",
            ),
            OpenApiParameter(
                name="verified",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Filter by email verification status",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Ordering field",
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Admin"],
        summary="Get User Details",
        description="Retrieve detailed information about a specific user.",
    ),
    update=extend_schema(
        tags=["Admin"], summary="Update User", description="Update user information."
    ),
    partial_update=extend_schema(
        tags=["Admin"],
        summary="Partial Update User",
        description="Partially update user information.",
    ),
    destroy=extend_schema(
        tags=["Admin"],
        summary="Delete User",
        description="Soft delete (deactivate) a user.",
    ),
    activate=extend_schema(
        tags=["Admin"], summary="Activate User", description="Activate a user account."
    ),
    deactivate=extend_schema(
        tags=["Admin"],
        summary="Deactivate User",
        description="Deactivate a user account.",
    ),
    assign_role=extend_schema(
        tags=["Admin"], summary="Assign Role", description="Assign a role to a user."
    ),
    remove_role=extend_schema(
        tags=["Admin"], summary="Remove Role", description="Remove a role from a user."
    ),
)
class AdminUserListViewSet(ModelViewSet):
    """
    Admin API viewset for listing and managing users.
    Provides paginated user listing with search, filtering, and admin actions.
    """

    queryset = User.objects.all()
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["username", "email", "fullname"]
    ordering_fields = ["date_joined", "email", "username"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        """Return different serializers based on action."""
        if self.action == "retrieve":
            return AdminUserDetailSerializer
        elif self.action in ["update", "partial_update"]:
            return AdminUserUpdateSerializer
        return AdminUserListSerializer

    def get_queryset(self):
        """
        Return filtered queryset based on admin permissions.
        Exclude the current admin user from the list.
        """
        qs = User.objects.all().exclude(id=self.request.user.id)

        # Additional filtering based on query parameters
        role_filter = self.request.query_params.get("role")
        if role_filter:
            qs = qs.filter(roles__name=role_filter)

        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)

        verified_filter = self.request.query_params.get("verified")
        if verified_filter == "true":
            qs = qs.filter(is_email_verified=True)
        elif verified_filter == "false":
            qs = qs.filter(is_email_verified=False)

        return qs.select_related().prefetch_related("roles")

    def list(self, request, *args, **kwargs):
        """
        List all users with pagination, search, and filtering support.
        """
        queryset = self.get_queryset()

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Users retrieved successfully",
                "count": queryset.count(),
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve specific user details for admin view.
        """
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(
            {"data": serializer.data, "message": "User details retrieved successfully"},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        """
        Update user details (admin action).
        """
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "User updated successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": serializer.errors, "message": "Failed to update user"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete user (deactivate) for admin action.
        """
        user = self.get_object()

        # Prevent admin from deleting themselves
        if user.id == request.user.id:
            return Response(
                {"message": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Soft delete by deactivating
        user.is_active = False
        user.save()

        return Response(
            {"message": "User deactivated successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a user account."""
        user = self.get_object()

        # Prevent admin from activating themselves
        if user.id == request.user.id:
            return Response(
                {"message": "Cannot modify your own account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        return Response(
            {"message": "User activated successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a user account."""
        user = self.get_object()

        # Prevent admin from deactivating themselves
        if user.id == request.user.id:
            return Response(
                {"message": "Cannot modify your own account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save()

        return Response(
            {"message": "User deactivated successfully"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def assign_role(self, request, pk=None):
        """Assign role to user."""
        user = self.get_object()
        role_name = request.data.get("role")

        if not role_name:
            return Response(
                {"message": "Role name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = Role.objects.get(name=role_name)
            user.roles.add(role)

            return Response(
                {"message": f"Role {role_name} assigned successfully"},
                status=status.HTTP_200_OK,
            )
        except Role.DoesNotExist:
            return Response(
                {"message": "Invalid role name"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"])
    def remove_role(self, request, pk=None):
        """Remove role from user."""
        user = self.get_object()
        role_name = request.data.get("role")

        if not role_name:
            return Response(
                {"message": "Role name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            role = Role.objects.get(name=role_name)
            user.roles.remove(role)

            return Response(
                {"message": f"Role {role_name} removed successfully"},
                status=status.HTTP_200_OK,
            )
        except Role.DoesNotExist:
            return Response(
                {"message": "Invalid role name"}, status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=["Admin"],
    summary="Get User Statistics",
    description="Retrieve user statistics for admin dashboard including total users, active users, admins, and recent signups.",
    examples=[
        OpenApiExample(
            "Success Response",
            value={
                "data": {
                    "total_users": 150,
                    "active_users": 142,
                    "inactive_users": 8,
                    "verified_users": 140,
                    "admin_count": 5,
                    "user_count": 145,
                    "recent_signups": 12,
                },
                "message": "User statistics retrieved successfully",
            },
            response_only=True,
        ),
    ],
)
class UserStatsView(APIView):
    """
    Get user statistics for admin dashboard.
    """

    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        verified_users = User.objects.filter(is_email_verified=True).count()

        # Count users by role
        admin_count = User.objects.filter(roles__name="admin").count()
        user_count = User.objects.filter(roles__name="user").count()

        # Recent signups (last 7 days)
        from datetime import timedelta

        from django.utils import timezone

        week_ago = timezone.now() - timedelta(days=7)
        recent_signups = User.objects.filter(date_joined__gte=week_ago).count()

        return Response(
            {
                "data": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": inactive_users,
                    "verified_users": verified_users,
                    "admin_count": admin_count,
                    "user_count": user_count,
                    "recent_signups": recent_signups,
                },
                "message": "User statistics retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )
