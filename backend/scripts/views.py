# views.py
import logging

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.mixins import MethodSpecificThrottleMixin
from payments.permissions import HasActiveSubscriptionPermission

from .filters import FullScriptFilter, ScriptOutlineFilter
from .models import FullScript, ScriptOutline, TemplateStyle, Tone
from .serializers import (
    FullScriptSerializer,
    GenerateOutlineRequestSerializer,
    GenerateOutlineResponseSerializer,
    GenerateScriptRequestSerializer,
    GenerateScriptResponseSerializer,
    ScriptGeneratorConfigResponseSerializer,
    ScriptOutlineSerializer,
    ScriptOutlineUpdateSerializer,
    TemplateStyleSerializer,
    ToneSerializer,
)
from .services.open_ai import OpenAIScriptService

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Get script generator configuration",
    description="Retrieve all configuration data needed for the script generator UI",
    responses={
        200: OpenApiResponse(
            response=ScriptGeneratorConfigResponseSerializer,
            description="Configuration data retrieved successfully",
        )
    },
)
@api_view(["GET"])
def script_generator_config(request):
    """
    Lightning-fast endpoint to get all config data for script generator UI
    """
    tones = Tone.objects.all().order_by("name")
    template_styles = TemplateStyle.objects.all().order_by("name")
    return Response(
        {
            "tones": ToneSerializer(tones, many=True).data,
            "template_styles": TemplateStyleSerializer(template_styles, many=True).data,
            "length_range": {"min": 0, "max": 10000, "default": 500},
        }
    )


@extend_schema(
    summary="Generate script outline",
    description="Generate a detailed script outline using OpenAI based on user input (description, tone, template style, length)",
    request=GenerateOutlineRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=GenerateOutlineResponseSerializer,
            description="Script outline generated successfully",
        ),
        400: OpenApiResponse(description="Invalid input data"),
        403: OpenApiResponse(description="Active subscription required"),
        500: OpenApiResponse(description="Outline generation failed"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def generate_script_outline(request):
    """
    Generate script outline using OpenAI from user input
    """
    # Get user input from request
    description = request.data.get("description")
    tone_id = request.data.get("tone")
    template_style_id = request.data.get("template_style")
    length = request.data.get("length", 500)
    title = request.data.get("title", "")

    if not description or not tone_id:
        return Response(
            {"error": "Description and tone are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Get tone and template style objects
        tone = Tone.objects.get(id=tone_id)
        template_style = None
        if template_style_id:
            template_style = TemplateStyle.objects.get(id=template_style_id)

        # Prepare script data for OpenAI
        script_data = {
            "description": description,
            "tone": tone.name,
            "template_style": template_style.name if template_style else "medium",
            "length": length,
        }

        # Generate outline
        outline_text, outline_data, metadata = OpenAIScriptService.generate_outline(
            script_data
        )

        # Create ScriptOutline directly (no intermediate Script record needed)
        outline = ScriptOutline.objects.create(
            title=f"Outline: {title or description[:50]}",
            outline_text=outline_text,
            outline_data=outline_data,
            original_outline=outline_text,
            status="generated",
            openai_model=metadata["model"],
            tokens_used=metadata["tokens_used"],
            generation_time=metadata["generation_time"],
        )

        serializer = ScriptOutlineSerializer(outline)
        return Response(
            {
                "outline": serializer.data,
                "message": "Script outline generated successfully!",
            },
            status=status.HTTP_201_CREATED,
        )

    except Tone.DoesNotExist:
        return Response(
            {"error": "Invalid tone selected"}, status=status.HTTP_400_BAD_REQUEST
        )
    except TemplateStyle.DoesNotExist:
        return Response(
            {"error": "Invalid template style selected"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Outline generation failed: {str(e)}")
        return Response(
            {"error": "Failed to generate outline. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="Get script outline",
    description="Retrieve a specific script outline by its UUID",
    responses={
        200: OpenApiResponse(description="Script outline retrieved successfully"),
        404: OpenApiResponse(description="Script outline not found"),
    },
)
class ScriptOutlineDetailView(
    MethodSpecificThrottleMixin, generics.RetrieveUpdateAPIView
):
    """
    Get and update script outline
    """

    queryset = ScriptOutline.objects.select_related("script", "script__tone")
    serializer_class = ScriptOutlineSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ScriptOutlineUpdateSerializer
        return ScriptOutlineSerializer

    @extend_schema(
        summary="Get script outline",
        description="Retrieve a specific script outline by its UUID",
        responses={
            200: OpenApiResponse(
                response=ScriptOutlineSerializer,
                description="Script outline retrieved successfully",
            ),
            404: OpenApiResponse(description="Script outline not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update script outline",
        description="Update a specific script outline by its UUID",
        request=ScriptOutlineUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=ScriptOutlineSerializer,
                description="Script outline updated successfully",
            ),
            404: OpenApiResponse(description="Script outline not found"),
            400: OpenApiResponse(description="Invalid input data"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@extend_schema(
    summary="Generate full script",
    description="Generate a complete script from an existing outline using OpenAI",
    request=GenerateScriptRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=GenerateScriptResponseSerializer,
            description="Full script generated successfully",
        ),
        404: OpenApiResponse(description="Script outline not found"),
        500: OpenApiResponse(description="Script generation failed"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def generate_full_script(request, outline_uuid):
    """
    Generate full script from outline
    """
    outline = get_object_or_404(ScriptOutline, uuid=outline_uuid)

    try:
        # Prepare data for OpenAI (we'll need to extract tone info from the outline or request)
        # For now, we'll use default values or get them from request
        tone_name = request.data.get("tone", "Informative")
        template_style_name = request.data.get("template_style", "medium")
        length = request.data.get("length", 5000)

        script_data = {
            "tone": tone_name,
            "template_style": template_style_name,
            "length": length,
        }

        # Generate full script
        script_content, sections, metadata = OpenAIScriptService.generate_full_script(
            outline.outline_text, script_data
        )

        # Create FullScript
        full_script = FullScript.objects.create(
            outline=outline,
            title=request.data.get("title", f"Script: {outline.title}"),
            content=script_content,
            sections=sections,
            status="generated",
            openai_model=metadata["model"],
            tokens_used=metadata["tokens_used"],
            generation_time=metadata["generation_time"],
        )

        # Update outline status
        outline.status = "script_generated"
        outline.save()

        serializer = FullScriptSerializer(full_script)
        return Response(
            {
                "script": serializer.data,
                "message": "Full script generated successfully!",
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Script generation failed: {str(e)}")
        return Response(
            {"error": "Failed to generate script. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class FullScriptDetailView(
    MethodSpecificThrottleMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    Full CRUD for full scripts
    """

    queryset = FullScript.objects.select_related("outline", "outline__script")
    serializer_class = FullScriptSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    @extend_schema(
        summary="Get full script",
        description="Retrieve a specific full script by its UUID",
        responses={
            200: OpenApiResponse(
                response=FullScriptSerializer,
                description="Full script retrieved successfully",
            ),
            404: OpenApiResponse(description="Full script not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update full script",
        description="Update a specific full script by its UUID",
        request=FullScriptSerializer,
        responses={
            200: OpenApiResponse(
                response=FullScriptSerializer,
                description="Full script updated successfully",
            ),
            404: OpenApiResponse(description="Full script not found"),
            400: OpenApiResponse(description="Invalid input data"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete full script",
        description="Delete a specific full script by its UUID",
        responses={
            204: OpenApiResponse(description="Full script deleted successfully"),
            404: OpenApiResponse(description="Full script not found"),
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="List all script outlines",
    description="Retrieve a paginated list of all script outlines with filtering options",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by title or content",
            required=False,
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by status (generating, generated, edited, approved, script_generated)",
            required=False,
        ),
        OpenApiParameter(
            name="filter_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by type: all, outline_drafts, script_drafts, saved",
            required=False,
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by field (created, modified, title). Use - for descending (e.g., -created)",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(description="Script outlines retrieved successfully")
    },
)
class ScriptOutlineListView(MethodSpecificThrottleMixin, generics.ListAPIView):
    """
    List all script outlines with filtering and search
    """

    serializer_class = ScriptOutlineSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ScriptOutlineFilter
    ordering_fields = ["created", "modified", "title"]
    ordering = ["-created"]
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    def get_queryset(self):
        return ScriptOutline.objects.select_related("script", "script__tone").order_by(
            "-created"
        )


@extend_schema(
    summary="List all full scripts",
    description="Retrieve a paginated list of all full scripts with filtering options",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by title or content",
            required=False,
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by status (generating, generated, edited, finalized, published)",
            required=False,
        ),
        OpenApiParameter(
            name="is_published",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter by published status",
            required=False,
        ),
        OpenApiParameter(
            name="filter_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by type: all, outline_drafts, script_drafts, saved",
            required=False,
        ),
        OpenApiParameter(
            name="word_count_min",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Minimum word count",
            required=False,
        ),
        OpenApiParameter(
            name="word_count_max",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Maximum word count",
            required=False,
        ),
        OpenApiParameter(
            name="duration_min",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Minimum estimated duration in minutes",
            required=False,
        ),
        OpenApiParameter(
            name="duration_max",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Maximum estimated duration in minutes",
            required=False,
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by field (created, modified, title, word_count, estimated_duration). Use - for descending (e.g., -created)",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=FullScriptSerializer(many=True),
            description="Full scripts retrieved successfully",
        )
    },
)
class FullScriptListView(MethodSpecificThrottleMixin, generics.ListAPIView):
    """
    List all full scripts with filtering and search
    """

    serializer_class = FullScriptSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = FullScriptFilter
    ordering_fields = [
        "created",
        "modified",
        "title",
        "word_count",
        "estimated_duration",
    ]
    ordering = ["-created"]
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    def get_queryset(self):
        return FullScript.objects.select_related("outline", "outline__script").order_by(
            "-created"
        )


@extend_schema(
    summary="Test script throttling",
    description="Test endpoint to demonstrate script API throttling with different rates for different HTTP methods",
    responses={
        200: OpenApiResponse(description="Throttling test successful"),
        429: OpenApiResponse(description="Rate limit exceeded"),
    },
)
class ThrottleTestView(MethodSpecificThrottleMixin, generics.GenericAPIView):
    """
    Test endpoint to demonstrate method-specific throttling.
    Different methods have different rate limits:
    - GET: 3/minute
    - POST: 20/minute
    - PUT: 20/minute
    - DELETE: 10/minute
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone

        return Response(
            {
                "message": f"Method-specific throttling test for {request.method} request",
                "method": request.method,
                "rate_limits": {
                    "GET": "3/minute",
                    "POST": "20/minute",
                    "PUT": "20/minute",
                    "DELETE": "10/minute",
                },
                "user": str(request.user),
                "user_type": "authenticated"
                if request.user.is_authenticated
                else "anonymous",
                "timestamp": timezone.now().isoformat(),
            }
        )

    def post(self, request):
        from django.utils import timezone

        return Response(
            {
                "message": f"Method-specific throttling test for {request.method} request",
                "method": request.method,
                "rate_limits": {
                    "GET": "3/minute",
                    "POST": "20/minute",
                    "PUT": "20/minute",
                    "DELETE": "10/minute",
                },
                "user": str(request.user),
                "user_type": "authenticated"
                if request.user.is_authenticated
                else "anonymous",
                "timestamp": timezone.now().isoformat(),
            }
        )

    def put(self, request):
        from django.utils import timezone

        return Response(
            {
                "message": f"Method-specific throttling test for {request.method} request",
                "method": request.method,
                "rate_limits": {
                    "GET": "3/minute",
                    "POST": "20/minute",
                    "PUT": "20/minute",
                    "DELETE": "10/minute",
                },
                "user": str(request.user),
                "user_type": "authenticated"
                if request.user.is_authenticated
                else "anonymous",
                "timestamp": timezone.now().isoformat(),
            }
        )

    def delete(self, request):
        from django.utils import timezone

        return Response(
            {
                "message": f"Method-specific throttling test for {request.method} request",
                "method": request.method,
                "rate_limits": {
                    "GET": "3/minute",
                    "POST": "20/minute",
                    "PUT": "20/minute",
                    "DELETE": "10/minute",
                },
                "user": str(request.user),
                "user_type": "authenticated"
                if request.user.is_authenticated
                else "anonymous",
                "timestamp": timezone.now().isoformat(),
            }
        )
