import logging
from datetime import datetime
import csv

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.openapi import OpenApiExample, OpenApiParameter, OpenApiResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from django.db.models import Count, Q, Prefetch
from django.utils.timezone import now, timedelta
from djstripe.models import Subscription
from django.utils.dateparse import parse_date
from django.http import HttpResponse

from admins.serializers import (
    AdminUserDetailSerializer,
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
    NichePacingSerializer,
    NicheSerializer,
    NicheToneSerializer,
    UserStatsResponseSerializer,
    FeatureUsageSerializer,
    StatsResponseSerializer,
    UserDetailsReportSerializer,
    UserConversionFunnelSerializer
)
from notifications.choices import NotificationType
from notifications.helpers import NotificationHelper
from scripts.pagination import GenerationsLimitOffsetPagination
from users.models import Role
from users.permissions import IsAdminPermission
from scripts.models import *
from payments.utils import get_active_subscription, get_or_create_customer
from payments.models import SubscriptionPlan

from .filters import NicheFilter, NichePacingFilter, NicheToneFilter
from .models import Niche, NichePacing, NicheTone

User = get_user_model()
logger = logging.getLogger(__name__)


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
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()
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
    serializer_class = UserStatsResponseSerializer

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
                "- `tone`: Filter niches by tone (e.g., 'Educational', 'Professional')\n"
                "- `pacing`: Filter niches by pacing (e.g., 'Fast', 'Slow')\n"
                "- `script_structure`: Filter niches by script structure keys or values (e.g., 'intro', 'body')\n"
                "- `best_for`: Filter niches by categories they are best suited for (e.g., 'Education', 'Gaming')\n"
                "- `ordering`: Order by field (e.g., 'created', '-created', 'title', '-title')\n\n"
                "**Note:** Each filter supports partial and case-insensitive matches. "
                "For example, `?tone=educ` will match both 'Educational' and 'Educative'."
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
                name="tone",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by tone (e.g., 'Educational', 'Neutral', 'Professional')",
            ),
            OpenApiParameter(
                name="pacing",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by pacing (e.g., 'Fast', 'Slow', 'Dynamic')",
            ),
            OpenApiParameter(
                name="script_structure",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by script structure content (e.g., 'intro', 'body', 'conclusion')",
            ),
            OpenApiParameter(
                name="best_for",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter by niche category (e.g., 'Education', 'Gaming', 'Technology')",
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
        ],
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

            # Create notification for new niche creation
            try:
                NotificationHelper.create_global_notification(
                    title="New Niche Added!",
                    message=f"A new niche '{niche.title}' has been added to TubeGenius. Check it out and start creating amazing scripts!",
                    notification_type=NotificationType.FEATURE,
                    metadata={
                        "niche": {
                            "label": niche.title,
                            "link": f"/niches?id={niche.id}",
                        },
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to create niche notification: {str(e)}")

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

            # Create notification for niche update
            try:
                NotificationHelper.create_global_notification(
                    title="Niche Updated!",
                    message=f"The niche '{updated_niche.title}' has been updated with new features and improvements. Explore the latest changes!",
                    notification_type=NotificationType.FEATURE,
                    metadata={
                        "niche": {
                            "label": updated_niche.title,
                            "link": f"/niches?id={updated_niche.id}",
                        },
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to create niche update notification: {str(e)}")

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
        niche_title = niche.title  # Store title before deletion

        # Create notification for niche deletion
        try:
            NotificationHelper.create_global_notification(
                title="Niche Removed",
                message=f"The niche '{niche_title}' has been removed from TubeGenius. Check out other available niches!",
                notification_type=NotificationType.FEATURE,
                metadata={
                    "niche": {
                        "label": niche_title,
                        "link": "/niches",
                    },
                },
            )
        except Exception as e:
            logger.warning(f"Failed to create niche deletion notification: {str(e)}")

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


@extend_schema(
    summary="Get platform statistics",
    description="Returns metrics: total users, new users this week, subscriber breakdown, and feature usage counts.",
    responses={200: StatsResponseSerializer},
    tags=["Admin"],
)
class StatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]

    def get(self, request):
        total_users = User.objects.count()
        new_users_this_week = User.objects.filter(created__gte=now() - timedelta(days=7)).count()

        # dj-stripe: Group active subscriptions by plan/price Nickname
        active_subs_query = (
            Subscription.objects
                .filter(status="active")
                .values("items__price__nickname", "items__price__product__name")  # Both nickname and product name
                .annotate(count=Count("id"))
        )
        subs_by_tier = {}
        for entry in active_subs_query:
            name = entry["items__price__nickname"] or entry["items__price__product__name"] or "Unnamed Plan"
            subs_by_tier[name] = entry["count"]

        script_count = FullScript.objects.count()
        title_count = UserTitles.objects.count()
        niche_count = Niche.objects.filter(status="active").count()

        return Response({
            "total_users": total_users,
            "new_users_this_week": new_users_this_week,
            "active_subscribers_by_plan": subs_by_tier,
            "feature_usage": {
                "script_generator": script_count,
                "title_generator": title_count,
                "niche_vault": niche_count
            }
        })


@extend_schema(
    tags=["Admin Report / Funnel"],
    summary="Get All Users Report",
    description=(
        "Retrieve report of all users with statistics including:\n"
        "- User details (Name/Email)\n"
        "- Total titles generated\n"
        "- Total short scripts generated\n"
        "- Total medium scripts generated\n"
        "- Total long scripts generated\n\n"
        "**Query Parameters:**\n"
        "- `start_date`: Filter users created from this date (YYYY-MM-DD format). Optional.\n"
        "- `end_date`: Filter users created until this date (YYYY-MM-DD format). Optional.\n"
        "- `format`: Set to 'csv' to export as CSV file.\n\n"
        "**Examples:**\n"
        "- Get all users: `/api/v1/admin/users-report/`\n"
        "- Get users created after start date: `/api/v1/admin/users-report/?start_date=2025-01-01`\n"
        "- Get users between two dates: `/api/v1/admin/users-report/?start_date=2025-01-01&end_date=2025-01-31`\n"
        "- Export filtered data as CSV: `/api/v1/admin/users-report/?start_date=2025-01-01&end_date=2025-01-31&format=csv`"
    ),
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created from this date (YYYY-MM-DD format). Optional.",
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created until this date (YYYY-MM-DD format). Optional.",
            required=False,
        ),
        OpenApiParameter(
            name="format",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Export format: csv (optional)",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="User details report retrieved successfully",
            response=UserDetailsReportSerializer,
        ),
    },
)
class UsersReportView(APIView):
    """
    Admin API to get report of all users with statistics.
    Supports filtering by start_date, end_date, and CSV export.
    """

    pagination_class = GenerationsLimitOffsetPagination

    def get(self, request):
        start_date_param = request.query_params.get("start_date")
        end_date_param = request.query_params.get("end_date")
        export_format = request.query_params.get("format", "").lower()

        queryset = User.objects.all()

        # Apply flexible date filtering
        if start_date_param or end_date_param:
            start_date = parse_date(start_date_param) if start_date_param else None
            end_date = parse_date(end_date_param) if end_date_param else None

            if start_date and end_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                queryset = queryset.filter(date_joined__range=(start_datetime, end_datetime))
            elif start_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                queryset = queryset.filter(date_joined__gte=start_datetime)
            elif end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                queryset = queryset.filter(date_joined__lte=end_datetime)
            else:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Annotate counts efficiently
        queryset = queryset.annotate(
            total_titles_generated=Count('user_titles', distinct=True),
            total_short_scripts=Count(
                'full_scripts',
                filter=Q(full_scripts__word_count__gte=2800, full_scripts__word_count__lte=3000),
                distinct=True
            ),
            total_medium_scripts=Count(
                'full_scripts',
                filter=Q(full_scripts__word_count__gte=5600, full_scripts__word_count__lte=6000),
                distinct=True
            ),
            total_long_scripts=Count(
                'full_scripts',
                filter=Q(full_scripts__word_count__gte=8400, full_scripts__word_count__lte=9000),
                distinct=True
            ),
        ).only('id', 'email', 'fullname', 'username')

        # Build report
        report_data = [
            {
                "name": user.fullname or user.username,
                "email": user.email,
                "total_titles_generated": user.total_titles_generated or 0,
                "total_short_scripts": user.total_short_scripts or 0,
                "total_medium_scripts": user.total_medium_scripts or 0,
                "total_long_scripts": user.total_long_scripts or 0,
            }
            for user in queryset
        ]

        # Handle CSV export
        if export_format == "csv":
            return self._export_csv(report_data, start_date_param, end_date_param)

        serializer = UserDetailsReportSerializer(report_data, many=True)
        return Response(
            {"data": serializer.data, "count": len(report_data), "message": "User details report retrieved successfully"},
            status=status.HTTP_200_OK,
        )

    def _export_csv(self, report_data, start_date_param, end_date_param):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if start_date_param or end_date_param:
            date_str = f"{start_date_param or 'NA'}_{end_date_param or 'NA'}".replace("-", "")
            filename = f"users_report_{date_str}_{timestamp}.csv"
        else:
            filename = f"users_report_all_{timestamp}.csv"

        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Total Titles", "Short Scripts", "Medium Scripts", "Long Scripts"])

        for row in report_data:
            writer.writerow([
                row["name"],
                row["email"],
                row["total_titles_generated"],
                row["total_short_scripts"],
                row["total_medium_scripts"],
                row["total_long_scripts"],
            ])

        return response


@extend_schema(
    tags=["Admin Report / Funnel"],
    summary="Export All Users Report as CSV",
    description=(
        "Export report of all users with statistics as CSV file including:\n"
        "- User details (Name/Email)\n"
        "- Total titles generated\n"
        "- Total short scripts generated\n"
        "- Total medium scripts generated\n"
        "- Total long scripts generated\n\n"
        "**Query Parameters:**\n"
        "- `start_date`: Filter users created from this date (YYYY-MM-DD format). Optional.\n"
        "- `end_date`: Filter users created until this date (YYYY-MM-DD format). Optional.\n\n"
        "**Examples:**\n"
        "- Export all users: `/api/v1/admin/users-report/export/`\n"
        "- Export users between two dates: `/api/v1/admin/users-report/export/?start_date=2025-01-01&end_date=2025-01-31`"
    ),
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created from this date (YYYY-MM-DD format). Optional.",
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created until this date (YYYY-MM-DD format). Optional.",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(description="CSV file downloaded successfully"),
    },
)
class UsersReportExportView(APIView):
    """
    Admin API to export user report as CSV.
    Supports filtering by start_date and end_date.
    """

    def get(self, request):
        start_date_param = request.query_params.get("start_date")
        end_date_param = request.query_params.get("end_date")

        queryset = User.objects.all()

        # Apply date range filter
        if start_date_param or end_date_param:
            start_date = parse_date(start_date_param) if start_date_param else None
            end_date = parse_date(end_date_param) if end_date_param else None

            if start_date and end_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                queryset = queryset.filter(date_joined__range=(start_datetime, end_datetime))
            elif start_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                queryset = queryset.filter(date_joined__gte=start_datetime)
            elif end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                queryset = queryset.filter(date_joined__lte=end_datetime)
            else:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        queryset = queryset.annotate(
            total_titles_generated=Count('user_titles', distinct=True),
            total_short_scripts=Count(
                'full_scripts',
                filter=Q(full_scripts__word_count__gte=2800, full_scripts__word_count__lte=3000),
                distinct=True
            ),
            total_medium_scripts=Count(
                'full_scripts',
                filter=Q(full_scripts__word_count__gte=5600, full_scripts__word_count__lte=6000),
                distinct=True
            ),
            total_long_scripts=Count(
                'full_scripts',
                filter=Q(full_scripts__word_count__gte=8400, full_scripts__word_count__lte=9000),
                distinct=True
            ),
        ).only('id', 'email', 'fullname', 'username')

        report_data = [
            {
                "name": user.fullname or user.username,
                "email": user.email,
                "total_titles_generated": user.total_titles_generated or 0,
                "total_short_scripts": user.total_short_scripts or 0,
                "total_medium_scripts": user.total_medium_scripts or 0,
                "total_long_scripts": user.total_long_scripts or 0,
            }
            for user in queryset
        ]

        return self._export_csv(report_data, start_date_param, end_date_param)

    def _export_csv(self, report_data, start_date_param, end_date_param):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if start_date_param or end_date_param:
            date_str = f"{start_date_param or 'NA'}_{end_date_param or 'NA'}".replace("-", "")
            filename = f"users_report_{date_str}_{timestamp}.csv"
        else:
            filename = f"users_report_all_{timestamp}.csv"

        response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'

        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Total Titles", "Short Scripts", "Medium Scripts", "Long Scripts"])

        for row in report_data:
            writer.writerow([
                row["name"],
                row["email"],
                row["total_titles_generated"],
                row["total_short_scripts"],
                row["total_medium_scripts"],
                row["total_long_scripts"],
            ])

        return response



# ... existing code ...

# Helper function to get customer without creating
import djstripe.models as djm


def get_customer_if_exists(user):
    """Get customer if exists, return None if not. Avoids creating unnecessary customers."""
    try:
        return djm.Customer.objects.filter(subscriber=user).first()
    except Exception:
        return None


def get_plan_name_from_subscription(subscription):
    """
    Get plan name from subscription.
    Handles multiple SubscriptionPlan entries with same stripe_price_id.
    Maps plan types to display names: Free Trial, Basic, Pro
    """
    plan_name = None
    plan_type = None

    try:
        if subscription and subscription.items.exists():
            first_item = subscription.items.first()
            if first_item and first_item.price:
                # Try to get local subscription plan - use filter().first() instead of get()
                try:
                    local_plans = SubscriptionPlan.objects.filter(
                        stripe_price_id=first_item.price.id
                    )
                    if local_plans.exists():
                        # Get the first matching plan (prefer active ones)
                        local_plan = local_plans.filter(is_active=True).first() or local_plans.first()
                        plan_name = local_plan.name
                        plan_type = local_plan.plan_type
                    else:
                        # Fallback to djstripe data
                        if first_item.price.product:
                            plan_name = first_item.price.product.name or "Unknown Plan"
                            plan_type = first_item.price.product.metadata.get("plan_type", "unknown")
                        else:
                            plan_name = "Unknown Plan"
                except Exception as e:
                    logger.warning(f"Error getting local plan: {e}")
                    # Fallback to djstripe data
                    if first_item.price.product:
                        plan_name = first_item.price.product.name or "Unknown Plan"
                        plan_type = first_item.price.product.metadata.get("plan_type", "unknown")
                    else:
                        plan_name = "Unknown Plan"
            else:
                plan_name = "No Plan Details"
        else:
            plan_name = "No Plan Items"
    except Exception as e:
        logger.warning(f"Error getting plan from subscription: {e}")
        plan_name = "Error Loading Plan"

    # Map plan types to display names
    plan_type_mapping = {
        "trial": "Free Trial",
        "basic": "Basic",
        "pro": "Pro",
    }

    # If plan_name contains the type, replace it; otherwise use plan_type mapping
    if plan_type and plan_type in plan_type_mapping:
        display_name = plan_type_mapping[plan_type]
        # If plan_name is just the type or generic, use the mapped name
        if not plan_name or plan_name.lower() in ["trial", "basic", "pro", "trial plan", "basic plan", "pro plan"]:
            plan_name = display_name
        elif display_name.lower() not in plan_name.lower():
            # If display name is not in plan_name, prepend or use display name
            plan_name = display_name

    return plan_name or "No Plan"


def get_subscription_status(subscription):
    """Get human-readable subscription status"""
    if not subscription:
        return "No Subscription"

    status = subscription.status
    # Map djstripe statuses to readable format
    status_mapping = {
        "active": "Active",
        "trialing": "Trial",
        "past_due": "Past Due",
        "canceled": "Canceled",
        "incomplete": "Incomplete",
        "incomplete_expired": "Expired",
        "unpaid": "Unpaid",
        "paused": "Paused",
    }

    return status_mapping.get(status, status.title() if status else "Unknown")


@extend_schema(
    tags=["Admin Report / Funnel"],
    summary="Get User Conversion Funnel",
    description=(
        "Retrieve conversion funnel data showing:\n"
        "- User signup information\n"
        "- Subscription plan status (Free Trial, Basic, Pro, or No Plan)\n"
        "- Subscription status (Active, Trial, Canceled, etc.)\n"
        "- User Active/Inactive status\n\n"
        "**Query Parameters:**\n"
        "- `start_date`: Filter users created on or after this date (YYYY-MM-DD).\n"
        "- `end_date`: Filter users created on or before this date (YYYY-MM-DD).\n\n"
        "**Examples:**\n"
        "- All users: `/api/v1/admin/conversion-funnel/`\n"
        "- From start date only: `/api/v1/admin/conversion-funnel/?start_date=2025-01-01`\n"
        "- Between range: `/api/v1/admin/conversion-funnel/?start_date=2025-01-01&end_date=2025-01-15`\n"
        "- Export CSV: `/api/v1/admin/conversion-funnel/export/?start_date=2025-01-01&end_date=2025-01-15`"
    ),
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created on or after this date (YYYY-MM-DD). Optional.",
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created on or before this date (YYYY-MM-DD). Optional.",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Conversion funnel data retrieved successfully",
        ),
    },
)
class UserConversionFunnelView(APIView):
    """
    Admin API to get user conversion funnel data.
    Supports filtering by start_date, end_date, or both.
    """

    def get(self, request):
        start_date_param = request.query_params.get("start_date")
        end_date_param = request.query_params.get("end_date")

        queryset = User.objects.all()

        # Apply date filters if provided
        if start_date_param or end_date_param:
            try:
                start_date = parse_date(start_date_param) if start_date_param else None
                end_date = parse_date(end_date_param) if end_date_param else None

                if start_date and end_date:
                    start_dt = datetime.combine(start_date, datetime.min.time())
                    end_dt = datetime.combine(end_date, datetime.max.time())
                    queryset = queryset.filter(date_joined__range=[start_dt, end_dt])
                elif start_date and not end_date:
                    start_dt = datetime.combine(start_date, datetime.min.time())
                    queryset = queryset.filter(date_joined__gte=start_dt)
                elif not start_date and end_date:
                    end_dt = datetime.combine(end_date, datetime.max.time())
                    queryset = queryset.filter(date_joined__lte=end_dt)
                else:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        queryset = queryset.only('id', 'email', 'fullname', 'username', 'is_active', 'date_joined')

        funnel_data = []
        for user in queryset:
            name = user.fullname or user.username
            email = user.email
            user_status = "Active" if user.is_active else "Inactive"
            subscription_plan = "No Plan"
            subscription_status = "No Subscription"

            customer = get_customer_if_exists(user)
            if customer:
                subscription = djm.Subscription.objects.filter(customer=customer).order_by("-created").first()
                if subscription:
                    subscription_plan = get_plan_name_from_subscription(subscription)
                    subscription_status = get_subscription_status(subscription)

            funnel_data.append({
                "name": name,
                "email": email,
                "subscription_plan": subscription_plan,
                "subscription_status": subscription_status,
                "status": user_status,
                "has_subscription": subscription_status not in ["No Subscription", "Canceled", "Expired"],
            })

        return Response({
            "data": funnel_data,
            "count": len(funnel_data),
            "message": "Conversion funnel data retrieved successfully"
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Admin Report / Funnel"],
    summary="Export User Conversion Funnel as CSV",
    description=(
        "Export conversion funnel data as CSV including:\n"
        "- User signup information\n"
        "- Subscription plan and status\n"
        "- Active/Inactive status\n\n"
        "**Query Parameters:**\n"
        "- `start_date`: Filter users created on or after this date (YYYY-MM-DD).\n"
        "- `end_date`: Filter users created on or before this date (YYYY-MM-DD).\n\n"
        "**Examples:**\n"
        "- Export all: `/api/v1/admin/conversion-funnel/export/`\n"
        "- Export by range: `/api/v1/admin/conversion-funnel/export/?start_date=2025-01-01&end_date=2025-01-15`"
    ),
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created on or after this date (YYYY-MM-DD). Optional.",
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter users created on or before this date (YYYY-MM-DD). Optional.",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(description="CSV file downloaded successfully"),
    },
)
class UserConversionFunnelExportView(APIView):
    """
    Admin API to export conversion funnel data as CSV.
    Supports start_date, end_date, or both.
    """

    def get(self, request):
        start_date_param = request.query_params.get("start_date")
        end_date_param = request.query_params.get("end_date")

        queryset = User.objects.all()

        if start_date_param or end_date_param:
            try:
                start_date = parse_date(start_date_param) if start_date_param else None
                end_date = parse_date(end_date_param) if end_date_param else None

                if start_date and end_date:
                    start_dt = datetime.combine(start_date, datetime.min.time())
                    end_dt = datetime.combine(end_date, datetime.max.time())
                    queryset = queryset.filter(date_joined__range=[start_dt, end_dt])
                elif start_date and not end_date:
                    start_dt = datetime.combine(start_date, datetime.min.time())
                    queryset = queryset.filter(date_joined__gte=start_dt)
                elif not start_date and end_date:
                    end_dt = datetime.combine(end_date, datetime.max.time())
                    queryset = queryset.filter(date_joined__lte=end_dt)
                else:
                    return Response(
                        {"error": "Invalid date format. Use YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        queryset = queryset.only('id', 'email', 'fullname', 'username', 'is_active', 'date_joined')

        funnel_data = []
        for user in queryset:
            name = user.fullname or user.username
            email = user.email
            user_status = "Active" if user.is_active else "Inactive"
            subscription_plan = "No Plan"
            subscription_status = "No Subscription"

            customer = get_customer_if_exists(user)
            if customer:
                subscription = djm.Subscription.objects.filter(customer=customer).order_by("-created").first()
                if subscription:
                    subscription_plan = get_plan_name_from_subscription(subscription)
                    subscription_status = get_subscription_status(subscription)

            funnel_data.append({
                "name": name,
                "email": email,
                "subscription_plan": subscription_plan,
                "subscription_status": subscription_status,
                "status": user_status,
            })

        return self._export_csv(funnel_data, start_date_param, end_date_param)

    def _export_csv(self, funnel_data, start_date_param, end_date_param):
        response = HttpResponse(content_type="text/csv; charset=utf-8")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "conversion_funnel_"

        if start_date_param and end_date_param:
            filename += f"{start_date_param}_to_{end_date_param}_"
        elif start_date_param:
            filename += f"from_{start_date_param}_"
        else:
            filename += "all_"

        filename += f"{timestamp}.csv"

        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(["Name", "Email", "Subscription Plan", "Subscription Status", "Active/Inactive Status"])

        for row in funnel_data:
            writer.writerow([row["name"], row["email"], row["subscription_plan"], row["subscription_status"], row["status"]])

        return response