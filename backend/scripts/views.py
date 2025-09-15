# views.py
from .models import Tone, TemplateStyle, ScriptOutline, FullScript
from .serializers import (
    ToneSerializer, TemplateStyleSerializer, ScriptOutlineUpdateSerializer,
    ScriptGeneratorConfigResponseSerializer, GenerateOutlineRequestSerializer,
    GenerateOutlineResponseSerializer, GenerateScriptRequestSerializer,
    GenerateScriptResponseSerializer, ScriptOutlineSerializer, FullScriptSerializer
)
from .filters import ScriptOutlineFilter, FullScriptFilter
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .services.open_ai import OpenAIScriptService
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Get script generator configuration",
    description="Retrieve all configuration data needed for the script generator UI",
    responses={
        200: OpenApiResponse(
            response=ScriptGeneratorConfigResponseSerializer,
            description="Configuration data retrieved successfully"
        )
    }
)
@api_view(['GET'])
def script_generator_config(request):
    """
    Lightning-fast endpoint to get all config data for script generator UI
    """
    tones = Tone.objects.all().order_by('name')
    template_styles = TemplateStyle.objects.all().order_by('name')
    return Response({
        'tones': ToneSerializer(tones, many=True).data,
        'template_styles': TemplateStyleSerializer(template_styles, many=True).data,
        'length_range': {
            'min': 0,
            'max': 10000,
            'default': 500
        }
    })


@extend_schema(
    summary="Generate script outline",
    description="Generate a detailed script outline using OpenAI based on user input (description, tone, template style, length)",
    request=GenerateOutlineRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=GenerateOutlineResponseSerializer,
            description="Script outline generated successfully"
        ),
        400: OpenApiResponse(description="Invalid input data"),
        500: OpenApiResponse(description="Outline generation failed")
    }
)
@api_view(['POST'])
def generate_script_outline(request):
    """
    Generate script outline using OpenAI from user input
    """
    # Get user input from request
    description = request.data.get('description')
    tone_id = request.data.get('tone')
    template_style_id = request.data.get('template_style')
    length = request.data.get('length', 500)
    title = request.data.get('title', '')

    if not description or not tone_id:
        return Response(
            {'error': 'Description and tone are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get tone and template style objects
        tone = Tone.objects.get(id=tone_id)
        template_style = None
        if template_style_id:
            template_style = TemplateStyle.objects.get(id=template_style_id)

        # Prepare script data for OpenAI
        script_data = {
            'description': description,
            'tone': tone.name,
            'template_style': template_style.name if template_style else 'medium',
            'length': length
        }

        # Generate outline
        outline_text, outline_data, metadata = OpenAIScriptService.generate_outline(script_data)

        # Create ScriptOutline directly (no intermediate Script record needed)
        outline = ScriptOutline.objects.create(
            title=f"Outline: {title or description[:50]}",
            outline_text=outline_text,
            outline_data=outline_data,
            original_outline=outline_text,
            status='generated',
            openai_model=metadata['model'],
            tokens_used=metadata['tokens_used'],
            generation_time=metadata['generation_time']
        )

        serializer = ScriptOutlineSerializer(outline)
        return Response({
            'outline': serializer.data,
            'message': 'Script outline generated successfully!'
        }, status=status.HTTP_201_CREATED)

    except Tone.DoesNotExist:
        return Response(
            {'error': 'Invalid tone selected'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except TemplateStyle.DoesNotExist:
        return Response(
            {'error': 'Invalid template style selected'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Outline generation failed: {str(e)}")
        return Response({
            'error': 'Failed to generate outline. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScriptOutlineDetailView(generics.RetrieveUpdateAPIView):
    """
    Get and update script outline
    """
    queryset = ScriptOutline.objects.select_related('script', 'script__tone')
    serializer_class = ScriptOutlineSerializer
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ScriptOutlineUpdateSerializer
        return ScriptOutlineSerializer

    @extend_schema(
        summary="Get script outline",
        description="Retrieve a specific script outline by its UUID",
        responses={
            200: OpenApiResponse(
                response=ScriptOutlineSerializer,
                description="Script outline retrieved successfully"
            ),
            404: OpenApiResponse(description="Script outline not found")
        }
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
                description="Script outline updated successfully"
            ),
            404: OpenApiResponse(description="Script outline not found"),
            400: OpenApiResponse(description="Invalid input data")
        }
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
            description="Full script generated successfully"
        ),
        404: OpenApiResponse(description="Script outline not found"),
        500: OpenApiResponse(description="Script generation failed")
    }
)
@api_view(['POST'])
def generate_full_script(request, outline_uuid):
    """
    Generate full script from outline
    """
    outline = get_object_or_404(ScriptOutline, uuid=outline_uuid)

    try:
        # Prepare data for OpenAI (we'll need to extract tone info from the outline or request)
        # For now, we'll use default values or get them from request
        tone_name = request.data.get('tone', 'Informative')
        template_style_name = request.data.get('template_style', 'medium')
        length = request.data.get('length', 5000)

        script_data = {
            'tone': tone_name,
            'template_style': template_style_name,
            'length': length
        }

        # Generate full script
        script_content, sections, metadata = OpenAIScriptService.generate_full_script(
            outline.outline_text, script_data
        )

        # Create FullScript
        full_script = FullScript.objects.create(
            outline=outline,
            title=request.data.get('title', f"Script: {outline.title}"),
            content=script_content,
            sections=sections,
            status='generated',
            openai_model=metadata['model'],
            tokens_used=metadata['tokens_used'],
            generation_time=metadata['generation_time']
        )

        # Update outline status
        outline.status = 'script_generated'
        outline.save()

        serializer = FullScriptSerializer(full_script)
        return Response({
            'script': serializer.data,
            'message': 'Full script generated successfully!'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Script generation failed: {str(e)}")
        return Response({
            'error': 'Failed to generate script. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FullScriptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Full CRUD for full scripts
    """
    queryset = FullScript.objects.select_related('outline', 'outline__script')
    serializer_class = FullScriptSerializer
    lookup_field = 'uuid'

    @extend_schema(
        summary="Get full script",
        description="Retrieve a specific full script by its UUID",
        responses={
            200: OpenApiResponse(
                response=FullScriptSerializer,
                description="Full script retrieved successfully"
            ),
            404: OpenApiResponse(description="Full script not found")
        }
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
                description="Full script updated successfully"
            ),
            404: OpenApiResponse(description="Full script not found"),
            400: OpenApiResponse(description="Invalid input data")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete full script",
        description="Delete a specific full script by its UUID",
        responses={
            204: OpenApiResponse(description="Full script deleted successfully"),
            404: OpenApiResponse(description="Full script not found")
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="List all script outlines",
    description="Retrieve a paginated list of all script outlines with filtering options",
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search by title or content',
            required=False
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by status (generating, generated, edited, approved, script_generated)',
            required=False
        ),
        OpenApiParameter(
            name='filter_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by type: all, outline_drafts, script_drafts, saved',
            required=False
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Order by field (created, modified, title). Use - for descending (e.g., -created)',
            required=False
        )
    ],
    responses={
        200: OpenApiResponse(
            response=ScriptOutlineSerializer(many=True),
            description="Script outlines retrieved successfully"
        )
    }
)
class ScriptOutlineListView(generics.ListAPIView):
    """
    List all script outlines with filtering and search
    """
    serializer_class = ScriptOutlineSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ScriptOutlineFilter
    ordering_fields = ['created', 'modified', 'title']
    ordering = ['-created']

    def get_queryset(self):
        return ScriptOutline.objects.select_related(
            'script', 'script__tone'
        ).order_by('-created')


@extend_schema(
    summary="List all full scripts",
    description="Retrieve a paginated list of all full scripts with filtering options",
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search by title or content',
            required=False
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by status (generating, generated, edited, finalized, published)',
            required=False
        ),
        OpenApiParameter(
            name='is_published',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filter by published status',
            required=False
        ),
        OpenApiParameter(
            name='filter_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by type: all, outline_drafts, script_drafts, saved',
            required=False
        ),
        OpenApiParameter(
            name='word_count_min',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Minimum word count',
            required=False
        ),
        OpenApiParameter(
            name='word_count_max',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Maximum word count',
            required=False
        ),
        OpenApiParameter(
            name='duration_min',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Minimum estimated duration in minutes',
            required=False
        ),
        OpenApiParameter(
            name='duration_max',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Maximum estimated duration in minutes',
            required=False
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Order by field (created, modified, title, word_count, estimated_duration). Use - for descending (e.g., -created)',
            required=False
        )
    ],
    responses={
        200: OpenApiResponse(
            response=FullScriptSerializer(many=True),
            description="Full scripts retrieved successfully"
        )
    }
)
class FullScriptListView(generics.ListAPIView):
    """
    List all full scripts with filtering and search
    """
    serializer_class = FullScriptSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = FullScriptFilter
    ordering_fields = ['created', 'modified', 'title', 'word_count', 'estimated_duration']
    ordering = ['-created']

    def get_queryset(self):
        return FullScript.objects.select_related(
            'outline', 'outline__script'
        ).order_by('-created')