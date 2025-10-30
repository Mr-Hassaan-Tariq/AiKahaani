from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admins.choices import NicheStatus
from admins.models import Niche
from admins.serializers import UserNicheListSerializer
from api.mixins import MethodSpecificThrottleMixin
from payments.permissions import HasPaidSubscriptionPermission
from scripts.pagination import GenerationsLimitOffsetPagination


@extend_schema(
    summary="List active niches",
    description="""
        Retrieve a paginated list of all active niches for authenticated users with active subscriptions.

        **Search:**
        - Use `search` parameter to search by title or tagline

        **Ordering:**
        - Use `ordering` parameter with: `title`, `created`, `modified`, `-title`, `-created`, `-modified`

        **Pagination:**
        - Use `limit` and `offset` parameters for pagination
    """,
    parameters=[
        OpenApiParameter(
            name="search",
            description="Search by title or tagline",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="ordering",
            description="Order by field (prefix with - for descending). Options: title, created, modified",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="limit",
            description="Number of results to return per page",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="offset",
            description="The initial index from which to return the results",
            required=False,
            type=int,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Active niches retrieved successfully",
            response=UserNicheListSerializer,
        ),
        403: OpenApiResponse(description="Active subscription required"),
    },
    tags=["Niches"],
)
class UserNicheListView(MethodSpecificThrottleMixin, generics.ListAPIView):
    """
    List all active niches for authenticated users with active subscriptions.

    Only returns niches with status='active'.
    Supports:
    - Search by title or tagline
    - Ordering by title, created, or modified date
    - Pagination using limit/offset parameters
    """

    serializer_class = UserNicheListSerializer
    permission_classes = [IsAuthenticated, HasPaidSubscriptionPermission]
    pagination_class = GenerationsLimitOffsetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "tagline"]
    ordering_fields = ["created", "modified", "title"]
    ordering = ["title"]  # Default ordering

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Niche.objects.none()
        return Niche.objects.filter(status=NicheStatus.ACTIVE)


@extend_schema(
    summary="Get niche details",
    description="""
        Retrieve details of a specific active niche by ID.

        Only active niches are accessible to users.
        Returns 404 if the niche doesn't exist or is not active.
    """,
    responses={
        200: OpenApiResponse(
            description="Niche details retrieved successfully",
            response=UserNicheListSerializer,
        ),
        404: OpenApiResponse(description="Niche not found or not active"),
        403: OpenApiResponse(description="Active subscription required"),
    },
    tags=["Niches"],
)
class UserNicheDetailView(MethodSpecificThrottleMixin, generics.RetrieveAPIView):
    """
    Retrieve details of a specific active niche by ID.

    Only returns niches with status='active'.
    Returns 404 if niche is not found or not active.
    """

    serializer_class = UserNicheListSerializer
    permission_classes = [IsAuthenticated, HasPaidSubscriptionPermission]
    lookup_field = "pk"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Niche.objects.none()
        return Niche.objects.filter(status=NicheStatus.ACTIVE)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to provide custom 404 message for inactive/missing niches."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Niche.DoesNotExist:
            return Response(
                {"detail": "Niche not found or not active."},
                status=status.HTTP_404_NOT_FOUND,
            )
