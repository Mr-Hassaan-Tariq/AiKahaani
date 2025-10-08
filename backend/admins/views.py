from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
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
from scripts.pagination import GenerationsLimitOffsetPagination
from users.models import Role
from users.permissions import IsAdminPermission

from .filters import NicheFilter, NichePacingFilter, NicheToneFilter
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
        queryset = self.filter_queryset(self.get_queryset())

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
        description=(
            "Retrieve a paginated list of niches with filtering and search capabilities.\n\n"
            "**Query Parameters:**\n"
            "- `limit`: Number of items to return (default: 20, max: 100)\n"
            "- `offset`: Number of items to skip (default: 0)\n"
            "- `search`: Search by title or tagline (custom search filter)\n"
            "- `status`: Filter by status (active/inactive)\n"
            "- `ordering`: Order by field (e.g., 'created', '-created', 'title', '-title')\n\n"
            "**Note:** The `search` parameter uses a custom filter that searches in both title and tagline fields."
        ),
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of items to return (default: 20, max: 100)",
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Number of items to skip (default: 0)",
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
                description="Ordering field (e.g., 'created', '-created', 'title')",
            ),
        ],
        examples=[
            OpenApiExample(
                name="List Niches Response",
                description="Example response showing paginated niches list",
                value={
                    "count": 25,
                    "next": "http://api.example.com/api/niches/?limit=20&offset=20",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "admin": 1,
                            "title": "Tech Reviews",
                            "tagline": "Latest tech product reviews",
                            "thumbnail": None,
                            "script_structure": {"intro": "Hook", "body": "Review"},
                            "tone": ["Educational", "Professional"],
                            "pacing": ["Fast", "Dynamic"],
                            "top_channels": [
                                {"name": "MKBHD", "link": "https://youtube.com/@mkbhd"}
                            ],
                            "best_for": ["Technology"],
                            "status": "active",
                            "created": "2025-01-15T10:30:00Z",
                            "modified": "2025-01-15T10:30:00Z",
                        },
                        {
                            "id": 2,
                            "admin": 1,
                            "title": "Gaming News",
                            "tagline": "Latest gaming updates",
                            "thumbnail": None,
                            "script_structure": None,
                            "tone": ["Casual", "Exciting"],
                            "pacing": ["Medium"],
                            "top_channels": [],
                            "best_for": ["Gaming", "Entertainment"],
                            "status": "active",
                            "created": "2025-01-14T09:20:00Z",
                            "modified": "2025-01-14T09:20:00Z",
                        },
                    ],
                },
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        tags=["Admin Niches"],
        summary="Create Niche",
        description=(
            "Create a new niche with detailed content structure.\n\n"
            "**Required Fields:**\n"
            "- `title` (string): The title of the niche\n"
            "- `tagline` (string): A brief tagline for the niche\n\n"
            "**Optional Fields:**\n"
            "- `thumbnail` (file): Image file for the niche thumbnail\n"
            "- `script_structure` (JSON object): Custom script structure configuration\n"
            "- `tone` (list of strings): List of tone names. Non-existent tones will be created automatically\n"
            "- `pacing` (list of strings): List of pacing names. Non-existent pacings will be created automatically\n"
            "- `top_channels` (list of objects): YouTube channels with name and link\n"
            "  - Each object must have: `name` (string) and `link` (string)\n"
            "- `best_for` (list of strings): Categories this niche is best suited for\n"
            "- `status` (string): Either 'active' or 'inactive' (default: 'active')\n\n"
            "**Note:** The `admin` field is automatically set to the authenticated user."
        ),
        examples=[
            OpenApiExample(
                name="Create Niche Example",
                description="Example of creating a tech review niche with all fields",
                value={
                    "title": "Tech Reviews",
                    "tagline": "Latest tech product reviews and analysis",
                    "tone": ["Educational", "Professional", "Engaging"],
                    "pacing": ["Fast", "Dynamic"],
                    "top_channels": [
                        {"name": "MKBHD", "link": "https://youtube.com/@mkbhd"},
                        {
                            "name": "Linus Tech Tips",
                            "link": "https://youtube.com/@LinusTechTips",
                        },
                    ],
                    "best_for": ["Technology", "Product Reviews", "Gadgets"],
                    "script_structure": {
                        "intro": "Hook with latest tech trend",
                        "body": "Detailed review",
                        "conclusion": "Recommendation",
                    },
                    "status": "active",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Minimal Create Example",
                description="Minimal example with only required fields",
                value={
                    "title": "Gaming News",
                    "tagline": "Latest gaming industry news and updates",
                },
                request_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Admin Niches"],
        summary="Get Niche Details",
        description="Retrieve detailed information about a specific niche by ID.",
        examples=[
            OpenApiExample(
                name="Niche Response Example",
                description="Example response showing niche details",
                value={
                    "data": {
                        "id": 1,
                        "admin": 1,
                        "title": "Tech Reviews",
                        "tagline": "Latest tech product reviews and analysis",
                        "thumbnail": None,
                        "script_structure": {
                            "intro": "Hook with latest tech trend",
                            "body": "Detailed review",
                            "conclusion": "Recommendation",
                        },
                        "tone": ["Educational", "Professional", "Engaging"],
                        "pacing": ["Fast", "Dynamic"],
                        "top_channels": [
                            {"name": "MKBHD", "link": "https://youtube.com/@mkbhd"}
                        ],
                        "best_for": ["Technology", "Product Reviews"],
                        "status": "active",
                        "created": "2025-01-15T10:30:00Z",
                        "modified": "2025-01-15T10:30:00Z",
                    },
                    "message": "Niche details retrieved successfully",
                },
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        tags=["Admin Niches"],
        summary="Update Niche",
        description=(
            "Update niche information. All fields from the create endpoint apply.\n\n"
            "**Important:**\n"
            "- Tones/pacings that don't exist will be created automatically\n"
            '- `top_channels` must follow the format: `[{"name": "...", "link": "..."}]`\n'
            "- All validations from the create endpoint apply"
        ),
        examples=[
            OpenApiExample(
                name="Update Niche Example",
                description="Example of updating a niche",
                value={
                    "title": "Tech Reviews - Updated",
                    "tagline": "Latest tech product reviews, analysis and comparisons",
                    "tone": ["Educational", "Professional", "Engaging", "Informative"],
                    "status": "active",
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=["Admin Niches"],
        summary="Partial Update Niche",
        description="Partially update niche information. Only provided fields will be updated.",
        examples=[
            OpenApiExample(
                name="Partial Update Example",
                description="Example of partially updating just the status",
                value={"status": "inactive"},
                request_only=True,
            ),
        ],
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NicheFilter
    search_fields = ["title", "tagline"]
    ordering_fields = ["created", "modified", "title"]
    ordering = ["-created"]
    pagination_class = GenerationsLimitOffsetPagination

    def get_queryset(self):
        """Return queryset with optimizations."""
        return Niche.objects.all().select_related("admin")

    def perform_create(self, serializer):
        """Set the admin field to the current user when creating a niche."""
        serializer.save(admin=self.request.user)

    def list(self, request, *args, **kwargs):
        """List all niches with pagination, search, and filtering support."""
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination using the configured pagination class
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback for when pagination is not configured
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @extend_schema(
        tags=["Admin Niches"],
        summary="Upload Niche Thumbnail",
        description=(
            "Upload a thumbnail image for a specific niche.\n\n"
            "**Parameters:**\n"
            "- `id`: The ID of the niche to update\n\n"
            "**Request Body:**\n"
            "- `thumbnail`: Image file (JPEG, PNG, GIF, WebP supported)\n\n"
            "**Response:**\n"
            "- Returns the updated niche data with the new thumbnail URL"
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "thumbnail": {
                        "type": "string",
                        "format": "binary",
                        "description": "Image file for the niche thumbnail",
                    }
                },
                "required": ["thumbnail"],
            }
        },
        examples=[
            OpenApiExample(
                name="Upload Thumbnail Request",
                description="Example of uploading a thumbnail image",
                value={"thumbnail": "<binary image file>"},
                request_only=True,
            ),
            OpenApiExample(
                name="Upload Thumbnail Response",
                description="Example response after successful thumbnail upload",
                value={
                    "data": {
                        "id": 1,
                        "admin": 1,
                        "title": "Tech Reviews",
                        "tagline": "Latest tech product reviews",
                        "thumbnail": "http://127.0.0.1:8000/media/niches/thumbnails/tech_review_thumb.jpg",
                        "script_structure": {"intro": "Hook", "body": "Review"},
                        "tone": ["Educational", "Professional"],
                        "pacing": ["Fast", "Dynamic"],
                        "top_channels": [],
                        "best_for": ["Technology"],
                        "status": "active",
                        "created": "2025-01-15T10:30:00Z",
                        "modified": "2025-01-15T10:30:00Z",
                    },
                    "message": "Thumbnail uploaded successfully",
                },
                response_only=True,
            ),
        ],
    )
    @action(detail=True, methods=["post"], url_path="upload-thumbnail")
    def upload_thumbnail(self, request, pk=None):
        """
        Upload thumbnail image for a niche.
        """
        try:
            niche = self.get_object()

            # Check if thumbnail file is provided
            if "thumbnail" not in request.FILES:
                return Response(
                    {"error": "No thumbnail file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            thumbnail_file = request.FILES["thumbnail"]

            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if thumbnail_file.content_type not in allowed_types:
                return Response(
                    {
                        "error": "Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate file size (5MB limit)
            max_size = 5 * 1024 * 1024  # 5MB in bytes
            if thumbnail_file.size > max_size:
                return Response(
                    {"error": "File size too large. Maximum size is 5MB."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the niche thumbnail
            niche.thumbnail = thumbnail_file
            niche.save()

            # Serialize and return the updated niche
            serializer = self.get_serializer(niche)

            return Response(
                {
                    "data": serializer.data,
                    "message": "Thumbnail uploaded successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to upload thumbnail: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NicheToneFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created"]
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        """List all niche tones."""
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination if configured
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NichePacingFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created"]
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        """List all niche pacings."""
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination if configured
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Niche pacings retrieved successfully",
                "count": queryset.count(),
            },
            status=status.HTTP_200_OK,
        )
