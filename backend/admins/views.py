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
    NichePacingSerializer,
    NicheSerializer,
    NicheToneSerializer,
)
from users.models import Role
from users.permissions import IsAdminPermission

from .models import Niche, NichePacing, NicheTone

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


@extend_schema_view(
    list=extend_schema(
        tags=["Admin Niches"],
        summary="List Niches",
        description="Retrieve a paginated list of niches with filtering and search capabilities.",
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
                description="Search by title or tagline",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by status (active/inactive)",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Ordering field",
            ),
        ],
    ),
    create=extend_schema(
        tags=["Admin Niches"],
        summary="Create Niche",
        description="Create a new niche with tone and pacing lists. Missing tones/pacings will be created automatically.",
    ),
    retrieve=extend_schema(
        tags=["Admin Niches"],
        summary="Get Niche Details",
        description="Retrieve detailed information about a specific niche.",
    ),
    update=extend_schema(
        tags=["Admin Niches"],
        summary="Update Niche",
        description="Update niche information with tone and pacing lists.",
    ),
    partial_update=extend_schema(
        tags=["Admin Niches"],
        summary="Partial Update Niche",
        description="Partially update niche information.",
    ),
    destroy=extend_schema(
        tags=["Admin Niches"],
        summary="Delete Niche",
        description="Delete a niche.",
    ),
)
class NicheViewSet(ModelViewSet):
    """
    Admin API viewset for managing niches.
    Provides CRUD operations with automatic tone/pacing creation and deduplication.
    """

    queryset = Niche.objects.all()
    serializer_class = NicheSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "tagline"]
    ordering_fields = ["created", "modified", "title"]
    ordering = ["-created"]

    def get_queryset(self):
        """Return filtered queryset based on query parameters."""
        qs = Niche.objects.all()

        # Additional filtering based on query parameters
        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            qs = qs.filter(status="active")
        elif status_filter == "inactive":
            qs = qs.filter(status="inactive")

        return qs.select_related("admin")

    def perform_create(self, serializer):
        """Set the admin field to the current user when creating a niche."""
        serializer.save(admin=self.request.user)

    def list(self, request, *args, **kwargs):
        """List all niches with pagination, search, and filtering support."""
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
                "message": "Niches retrieved successfully",
                "count": queryset.count(),
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """Create a new niche with tone/pacing creation and deduplication."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            niche = serializer.save(admin=request.user)
            return Response(
                {
                    "data": NicheSerializer(niche).data,
                    "message": "Niche created successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors, "message": "Failed to create niche"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve specific niche details."""
        niche = self.get_object()
        serializer = self.get_serializer(niche)
        return Response(
            {
                "data": serializer.data,
                "message": "Niche details retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        """Update niche details with tone/pacing creation and deduplication."""
        niche = self.get_object()
        serializer = self.get_serializer(
            niche, data=request.data, partial=kwargs.get("partial", False)
        )

        if serializer.is_valid():
            updated_niche = serializer.save()
            return Response(
                {
                    "data": NicheSerializer(updated_niche).data,
                    "message": "Niche updated successfully",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"errors": serializer.errors, "message": "Failed to update niche"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a niche."""
        niche = self.get_object()
        niche.delete()
        return Response(
            {"message": "Niche deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Admin Niches"],
        summary="List Niche Tones",
        description="Retrieve a list of all niche tones.",
    ),
    create=extend_schema(
        tags=["Admin Niches"],
        summary="Create Niche Tone",
        description="Create a new niche tone.",
    ),
)
class NicheToneViewSet(ModelViewSet):
    """
    Admin API viewset for managing niche tones.
    """

    queryset = NicheTone.objects.all()
    serializer_class = NicheToneSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created"]
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        """List all niche tones."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Niche tones retrieved successfully",
                "count": queryset.count(),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Admin Niches"],
        summary="List Niche Pacings",
        description="Retrieve a list of all niche pacings.",
    ),
    create=extend_schema(
        tags=["Admin Niches"],
        summary="Create Niche Pacing",
        description="Create a new niche pacing.",
    ),
)
class NichePacingViewSet(ModelViewSet):
    """
    Admin API viewset for managing niche pacings.
    """

    queryset = NichePacing.objects.all()
    serializer_class = NichePacingSerializer
    permission_classes = [IsAuthenticated, IsAdminPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created"]
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        """List all niche pacings."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Niche pacings retrieved successfully",
                "count": queryset.count(),
            },
            status=status.HTTP_200_OK,
        )
