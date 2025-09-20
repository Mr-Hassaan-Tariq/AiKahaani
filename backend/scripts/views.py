# views.py
import logging
import os
from datetime import datetime

from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import MethodSpecificThrottleMixin
from payments.permissions import HasActiveSubscriptionPermission

from .filters import FullScriptFilter, ScriptOutlineFilter, generation_filters
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
    StatusUpdateSerializer,
    TemplateStyleSerializer,
    ToneSerializer,
    UnifiedGenerationSerializer,
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
    description="""Generate a detailed script outline using multiple tones.

**Three input methods supported:**
1. **Text Description (JSON)**: Provide a text description in JSON format
2. **Image Upload (Form Data)**: Upload an image file using multipart/form-data
3. **Image URL**: Provide an image URL that will be analyzed

**Usage:**
- For text input: Use `Content-Type: application/json` with `description` field
- For image file: Use `Content-Type: multipart/form-data` with `image` file
- For image URL: Use either JSON or form data with `image_url` field
- Either `description`, `image` file, or `image_url` must be provided (only one)
- **When providing an image**: No need to provide title or description - they will be automatically generated from the image content using OpenAI Vision""",
    request={
        "multipart/form-data": GenerateOutlineRequestSerializer,
        "application/json": GenerateOutlineRequestSerializer,
    },
    responses={
        201: OpenApiResponse(
            response=GenerateOutlineResponseSerializer,
            description="Script outline generated successfully",
        ),
        400: OpenApiResponse(
            description="Invalid input data - either description or image must be provided"
        ),
        403: OpenApiResponse(description="Active subscription required"),
        500: OpenApiResponse(description="Outline generation or image analysis failed"),
    },
    examples=[
        OpenApiExample(
            "Text Description (JSON)",
            value={
                "description": "How to learn Python programming from scratch",
                "tones": [1],
                "template_style": 2,
                "min_length": 200,
                "max_length": 800,
                "title": "Python Learning Guide",
            },
            media_type="application/json",
        ),
        OpenApiExample(
            "Image Upload (Form Data)",
            value={
                "tones": [1, 3],
                "template_style": 1,
                "min_length": 300,
                "max_length": 1000,
                "image": "[Upload image file here]",
            },
            media_type="multipart/form-data",
        ),
        OpenApiExample(
            "Image URL (JSON)",
            value={
                "tones": [1, 2],
                "template_style": 2,
                "min_length": 200,
                "max_length": 800,
                "image_url": "https://example.com/path/to/image.jpg",
            },
            media_type="application/json",
        ),
    ],
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def generate_script_outline(request):
    serializer = GenerateOutlineRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    description = validated_data.get("description", "")
    image = validated_data.get("image")
    image_url = validated_data.get("image_url", "")
    tone_ids = validated_data["tones"]
    template_style_id = validated_data.get("template_style")
    min_length = validated_data.get("min_length", 100)
    max_length = validated_data.get("max_length", 1000)
    title = validated_data.get("title", "")

    if image or image_url:
        try:
            if image:
                if hasattr(image, "read") and hasattr(image, "seek"):
                    image_title, image_description = OpenAIScriptService.analyze_image(
                        image_file=image
                    )
                else:
                    return Response(
                        {"error": "Invalid image file."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                image_title, image_description = OpenAIScriptService.analyze_image(
                    image_url=image_url
                )

            title = image_title
            description = image_description

        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return Response(
                {"error": "Failed to analyze the provided image."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    try:
        tones = Tone.objects.filter(id__in=tone_ids)
        if len(tones) != len(tone_ids):
            return Response(
                {"error": "One or more invalid tone IDs provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        template_style = None
        if template_style_id:
            template_style = TemplateStyle.objects.get(id=template_style_id)

        script_data = {
            "description": description,
            "tones": [tone.name for tone in tones],
            "template_style": template_style.name if template_style else "medium",
            "min_length": min_length,
            "max_length": max_length,
        }

        outline_text, outline_data, metadata = OpenAIScriptService.generate_outline(
            script_data
        )

        outline_title = title if title else f"Outline: {description[:50]}"
        outline = ScriptOutline.objects.create(
            user=request.user,
            title=outline_title,
            outline_text=outline_text,
            outline_data=outline_data,
            original_outline=outline_text,
            status="generated",
            openai_model=metadata["model"],
            tokens_used=metadata["tokens_used"],
            generation_time=metadata["generation_time"],
        )
        outline.tones.set(tones)

        serializer = ScriptOutlineSerializer(outline)
        return Response(
            {
                "outline": serializer.data,
                "message": "Script outline generated successfully!",
            },
            status=status.HTTP_201_CREATED,
        )

    except TemplateStyle.DoesNotExist:
        return Response(
            {"error": "Invalid template style selected"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Outline generation failed: {str(e)}")
        return Response(
            {"error": "Failed to generate outline."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    summary="Recreate script outline",
    description="Recreate an existing script outline using the same parameters as the original. This will generate a new outline with the same tones, template style, and length parameters, but with fresh AI-generated content.",
    responses={
        201: OpenApiResponse(
            response=GenerateOutlineResponseSerializer,
            description="Script outline recreated successfully",
        ),
        404: OpenApiResponse(description="Original outline not found or access denied"),
        403: OpenApiResponse(description="Active subscription required"),
        500: OpenApiResponse(description="Outline recreation failed"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def recreate_script_outline(request, uuid):
    """
    Recreate a script outline using the same parameters as an existing outline.

    This endpoint takes the UUID of an existing outline and generates a new outline
    using the same parameters (tones, template style, description, etc.) but with
    fresh AI-generated content.
    """
    # Get the original outline, ensuring it belongs to the requesting user
    try:
        original_outline = ScriptOutline.objects.get(uuid=uuid, user=request.user)
    except ScriptOutline.DoesNotExist:
        return Response(
            {"error": "Outline not found or access denied"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        # Extract parameters from the original outline
        # We'll need to reconstruct the original parameters used for generation

        # Get tones from the original outline
        tones = list(original_outline.tones.all())
        if not tones:
            return Response(
                {"error": "Cannot recreate outline: original outline has no tones"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try to extract template style from the script if it exists
        template_style = None
        if original_outline.script and original_outline.script.template_style:
            template_style = original_outline.script.template_style

        # Use default length parameters (we could store these in outline_data if needed)
        min_length = 100
        max_length = 1000

        # Try to extract length parameters from outline_data if available
        if original_outline.outline_data:
            min_length = original_outline.outline_data.get("min_length", 100)
            max_length = original_outline.outline_data.get("max_length", 1000)

        # Extract description from the original outline
        # This could be stored in outline_data or we might need to use the title
        description = (
            original_outline.outline_data.get("description", "")
            if original_outline.outline_data
            else ""
        )
        if not description:
            # Fallback to using the title or outline text as description
            description = (
                original_outline.title
                or f"Recreate outline based on: {original_outline.outline_text[:100]}..."
            )

        # Prepare script data for OpenAI service
        script_data = {
            "description": description,
            "tones": [tone.name for tone in tones],
            "template_style": template_style.name if template_style else "medium",
            "min_length": min_length,
            "max_length": max_length,
        }

        # Generate new outline using OpenAI service
        outline_text, outline_data, metadata = OpenAIScriptService.generate_outline(
            script_data
        )

        # Create new outline with "Recreated" prefix
        new_title = (
            f"Recreated: {original_outline.title}"
            if original_outline.title
            else f"Recreated outline from {original_outline.uuid}"
        )

        new_outline = ScriptOutline.objects.create(
            user=request.user,
            title=new_title,
            outline_text=outline_text,
            outline_data=outline_data,
            original_outline=outline_text,
            status="generated",
            openai_model=metadata["model"],
            tokens_used=metadata["tokens_used"],
            generation_time=metadata["generation_time"],
        )

        # Set the same tones as the original
        new_outline.tones.set(tones)

        serializer = ScriptOutlineSerializer(new_outline)
        return Response(
            {
                "outline": serializer.data,
                "message": f"Script outline recreated successfully from original outline {original_outline.uuid}!",
                "original_outline_uuid": str(original_outline.uuid),
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Outline recreation failed: {str(e)}")
        return Response(
            {"error": "Failed to recreate outline. Please try again."},
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
    MethodSpecificThrottleMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    Get and update script outline
    """

    serializer_class = ScriptOutlineSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    def get_queryset(self):
        return (
            ScriptOutline.objects.filter(user=self.request.user)
            .select_related("script")
            .prefetch_related("script__tones", "tones")
        )

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
        summary="Delete script outline",
        description="Delete a specific script outline by its UUID",
        responses={
            200: OpenApiResponse(description="Script outline deleted successfully"),
            404: OpenApiResponse(description="Script outline not found"),
        },
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Script outline deleted successfully"}, 
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Generate full script",
    description="Generate a complete script from an existing outline. The script will use the tones from the outline, or fallback to the provided tone if the outline has no tones.",
    request=GenerateScriptRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=GenerateScriptResponseSerializer,
            description="Full script generated successfully",
        ),
        404: OpenApiResponse(description="Script outline not found"),
        500: OpenApiResponse(description="Script generation failed"),
    },
    examples=[
        OpenApiExample(
            "Full Script Example",
            value={
                "tone": "Informative",
                "template_style": "medium",
                "min_length": 1500,
                "max_length": 3000,
                "title": "Complete Python Tutorial",
            },
        )
    ],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def generate_full_script(request, uuid):
    """
    Generate full script from outline
    """
    outline = get_object_or_404(ScriptOutline, uuid=uuid, user=request.user)

    try:
        # Get tones from the outline or use request data as fallback
        outline_tones = [tone.name for tone in outline.tones.all()]
        if not outline_tones:
            # Fallback to request data if outline has no tones
            tone_name = request.data.get("tone", "Informative")
            outline_tones = [tone_name]

        template_style_name = request.data.get("template_style", "medium")
        min_length = request.data.get("min_length", 1000)
        max_length = request.data.get("max_length", 5000)

        script_data = {
            "tones": outline_tones,
            "template_style": template_style_name,
            "min_length": min_length,
            "max_length": max_length,
        }

        # Generate full script
        script_content, sections, metadata = OpenAIScriptService.generate_full_script(
            outline.outline_text, script_data
        )

        # Create FullScript
        full_script = FullScript.objects.create(
            user=request.user,
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
        outline.status = "saved"
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

    serializer_class = FullScriptSerializer
    lookup_field = "uuid"
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    def get_queryset(self):
        return FullScript.objects.filter(user=self.request.user).select_related(
            "outline", "outline__script"
        )

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
        return (
            ScriptOutline.objects.filter(user=self.request.user)
            .select_related("script")
            .prefetch_related("script__tones", "tones")
            .order_by("-created")
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
        return (
            FullScript.objects.filter(user=self.request.user)
            .select_related("outline", "outline__script")
            .order_by("-created")
        )


@extend_schema(
    summary="List all generations (unified)",
    description="""
    Retrieve a unified list of both script outlines and full scripts with comprehensive filtering and sorting options.
    
    **Filter Combinations:**
    - Use `type=script` to apply word_count and duration filters only to scripts
    - Use `type=outline` to get only outlines (word_count/duration filters ignored)
    - Combine multiple filters for precise results
    
    **Examples:**
    - `?type=script&word_count_min=500&duration_max=10` - Scripts with 500+ words, max 10 min
    - `?filter_type=saved&search=tutorial` - Saved items containing 'tutorial'
    - `?status=generated&ordering=-modified` - Generated items, newest first
    """,
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
            description="Filter by status (draft, generated, saved)",
            required=False,
        ),
        OpenApiParameter(
            name="filter_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by type: "all" (default), "outline_drafts" (draft/generated outlines only), "script_drafts" (draft/generated scripts only), "saved" (saved items only)',
            required=False
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by generation type: "outline" (outlines only), "script" (scripts only). Use "script" to apply word_count/duration filters effectively.',
            required=False
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by field (created, modified, title). Use - for descending (e.g., -created)",
            required=False,
        ),
        OpenApiParameter(
            name="word_count_min",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Minimum word count for scripts (only applies to scripts, outlines are unaffected). Example: 500',
            required=False
        ),
        OpenApiParameter(
            name="word_count_max",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Maximum word count for scripts (only applies to scripts, outlines are unaffected). Example: 2000',
            required=False
        ),
        OpenApiParameter(
            name="duration_min",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Minimum estimated video duration in minutes (only applies to scripts, outlines are unaffected). Example: 3.5',
            required=False
        ),
        OpenApiParameter(
            name="duration_max",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Maximum estimated video duration in minutes (only applies to scripts, outlines are unaffected). Example: 15.0',
            required=False
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ScriptOutlineSerializer(many=True),
            description="Script outlines retrieved successfully",
        )
    },
)
class ScriptOutlineListView(generics.ListAPIView):
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
        return (
            ScriptOutline.objects.filter(user=self.request.user)
            .select_related("script")
            .prefetch_related("script__tones", "tones")
            .order_by("-created")
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
class FullScriptListView(generics.ListAPIView):
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
        return (
            FullScript.objects.filter(user=self.request.user)
            .select_related("outline", "outline__script")
            .order_by("-created")
        )


@extend_schema(
    summary="List all generations (unified)",
    description="Retrieve a unified list of both script outlines and full scripts with filtering and sorting options. This endpoint combines both outlines and scripts into a single response with consistent formatting.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by title or content across both outlines and scripts",
            required=False,
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by status: draft, generated, saved",
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
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by generation type: outline, script",
            required=False,
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by field: created, modified, title, word_count, estimated_duration. Use - for descending (e.g., -created)",
            required=False,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=UnifiedGenerationSerializer(many=True),
            description="Generations retrieved successfully",
        ),
        404: OpenApiResponse(description="No generations found for the given filters"),
        400: OpenApiResponse(description="Invalid filter parameters"),
    },
)
class GenerationsList(APIView):
    """
    Unified listing API for both outlines and scripts.
    Handles filtering, sorting, and returning data for both outlines and scripts.
    """

    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    def get(self, request):
        """
        Handles GET requests for unified outlines and scripts.
        Allows filtering and sorting of the results based on the provided query parameters.
        """
        # Get filter parameters from request
        search = request.GET.get("search", "")
        status_filter = request.GET.get("status", "")
        filter_type = request.GET.get("filter_type", "all")
        type_filter = request.GET.get("type", "")
        ordering = request.GET.get("ordering", "-created")

        # Get numeric filters
        word_count_min = request.GET.get("word_count_min")
        word_count_max = request.GET.get("word_count_max")
        duration_min = request.GET.get("duration_min")
        duration_max = request.GET.get("duration_max")

        # Convert to integers if provided
        try:
            word_count_min = int(word_count_min) if word_count_min else None
        except (ValueError, TypeError):
            word_count_min = None

        try:
            word_count_max = int(word_count_max) if word_count_max else None
        except (ValueError, TypeError):
            word_count_max = None

        try:
            duration_min = float(duration_min) if duration_min else None
        except (ValueError, TypeError):
            duration_min = None

        try:
            duration_max = float(duration_max) if duration_max else None
        except (ValueError, TypeError):
            duration_max = None

        filtered_querysets = generation_filters(
            search,
            status_filter,
            filter_type,
            type_filter,
            ordering,
            user=request.user,
            word_count_min=word_count_min,
            word_count_max=word_count_max,
            duration_min=duration_min,
            duration_max=duration_max,
        )
        serializer = UnifiedGenerationSerializer(filtered_querysets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Update outline status",
    description="Update the status of a script outline",
    request=StatusUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=ScriptOutlineSerializer,
            description="Outline status updated successfully",
        ),
        404: OpenApiResponse(description="Outline not found"),
        400: OpenApiResponse(description="Invalid status"),
    },
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def update_outline_status(request, outline_uuid):
    """
    Update the status of a script outline
    """
    outline = get_object_or_404(ScriptOutline, uuid=outline_uuid, user=request.user)

    serializer = StatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        outline.status = serializer.validated_data["status"]
        outline.save()

        response_serializer = ScriptOutlineSerializer(outline)
        return Response(response_serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Update script status",
    description="Update the status of a full script",
    request=StatusUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=FullScriptSerializer,
            description="Script status updated successfully",
        ),
        404: OpenApiResponse(description="Script not found"),
        400: OpenApiResponse(description="Invalid status"),
    },
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, HasActiveSubscriptionPermission])
def update_script_status(request, script_uuid):
    """
    Update the status of a full script
    """
    script = get_object_or_404(FullScript, uuid=script_uuid, user=request.user)

    serializer = StatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        script.status = serializer.validated_data["status"]
        script.save()

        response_serializer = FullScriptSerializer(script)
        return Response(response_serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Export script to file",
    description="Export a full script to various file formats (.txt, .pdf, .docx). The file will be downloaded with appropriate headers.",
    parameters=[
        OpenApiParameter(
            name="format",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Export format: txt, pdf, or docx",
            required=True,
            enum=["txt", "pdf", "docx"],
        ),
    ],
    responses={
        200: OpenApiResponse(description="File exported successfully"),
        400: OpenApiResponse(description="Invalid format specified"),
        404: OpenApiResponse(description="Script not found or access denied"),
        403: OpenApiResponse(description="Active subscription required"),
    },
)
class ExportScriptView(APIView):
    """
    Export a full script to various file formats

    Supported formats:
    - txt: Plain text format
    - pdf: PDF format with proper formatting
    - docx: Microsoft Word document format
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # return Response({"message": "Export request received"}, status=status.HTTP_200_OK)
        """Handle GET request to export script in specified format"""
        # Debug logging
        logger.info(f"Export request received for UUID: {kwargs['uuid']}")
        logger.info(f"User: {request.user}")
        logger.info(f"Format: {request.data.get('format', 'not provided')}")

        # Get the format parameter
        export_format = request.data.get("format", "").lower()
        if export_format not in ["txt", "pdf", "docx"]:
            return Response(
                {"error": "Invalid format. Supported formats: txt, pdf, docx"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the script, ensuring it belongs to the requesting user
        try:
            script = FullScript.objects.get(uuid=kwargs["uuid"], user=request.user)
            logger.info(f"Script found: {script.title}")
        except FullScript.DoesNotExist:
            # Enhanced error logging
            logger.error(
                f"Script not found for UUID: {kwargs['uuid']}, User: {request.user}"
            )

            # Check if script exists for any user
            try:
                script_exists = FullScript.objects.get(uuid=kwargs["uuid"])
                logger.error(
                    f"Script exists but belongs to different user: {script_exists.user}"
                )
                return Response(
                    {
                        "error": "Script not found or access denied",
                        "debug": "Script exists but access denied",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            except FullScript.DoesNotExist:
                logger.error(f"Script with UUID {kwargs['uuid']} does not exist at all")
                return Response(
                    {
                        "error": "Script not found or access denied",
                        "debug": "Script does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(
                c for c in script.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_title = safe_title.replace(" ", "_")[
                :50
            ]  # Limit length and replace spaces

            if export_format == "txt":
                result = _export_txt(script, safe_title, timestamp)
            elif export_format == "pdf":
                result = _export_pdf(script, safe_title, timestamp)
            elif export_format == "docx":
                result = _export_docx(script, safe_title, timestamp)
            result = request.build_absolute_uri(result["file_url"])
            return Response({"file_url": result}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Script export failed: {str(e)}")
            return Response(
                {"error": "Failed to export script. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def _export_txt(script, safe_title, timestamp):
    """Export script as plain text file and save to media folder"""
    content = f"Title: {script.title}\n"
    content += f"Created: {script.created.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"Word Count: {script.word_count}\n"
    content += f"Estimated Duration: {script.estimated_duration:.1f} minutes\n"
    content += "=" * 50 + "\n\n"
    content += script.content

    filename = f"{safe_title}_{timestamp}.txt"
    filepath = os.path.join("exports", filename)  # subfolder in MEDIA_ROOT

    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    file_url = settings.MEDIA_URL + filepath
    return {"file_url": file_url}


def _export_pdf(script, safe_title, timestamp):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    # CAN BE BETTER IMPLEMENTED
    filename = f"{safe_title}_{timestamp}.pdf"
    filepath = os.path.join("exports", filename)
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Write PDF to disk
    doc = SimpleDocTemplate(
        full_path, pagesize=A4, topMargin=1 * inch, bottomMargin=1 * inch
    )
    styles = getSampleStyleSheet()
    story = [Paragraph(script.title, styles["Heading1"]), Spacer(1, 12)]
    story.append(Paragraph(script.content, styles["Normal"]))
    doc.build(story)

    file_url = settings.MEDIA_URL + filepath
    return {"file_url": file_url}


def _export_docx(script, safe_title, timestamp):
    from docx import Document

    filename = f"{safe_title}_{timestamp}.docx"
    filepath = os.path.join("exports", filename)
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    doc = Document()
    doc.add_heading(script.title, 0)
    doc.add_paragraph(script.content)
    doc.save(full_path)
    # TODO: Add file to storage/DELETE AFTER 10 MINUTES
    file_url = settings.MEDIA_URL + filepath
    return {"file_url": file_url}
