# views.py
from .models import Tone, TemplateStyle, ScriptOutline, FullScript
from .serializers import (
    ToneSerializer, TemplateStyleSerializer, ScriptOutlineUpdateSerializer
)
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .services.open_ai import OpenAIScriptService
from .serializers import ScriptOutlineSerializer, FullScriptSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Get script generator configuration",
    description="Retrieve all configuration data needed for the script generator UI",
    responses={
        200: OpenApiResponse(description="Configuration data retrieved successfully")
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
    responses={
        201: OpenApiResponse(description="Script outline generated successfully"),
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


@extend_schema(
    summary="Get script outline",
    description="Retrieve a specific script outline by its UUID",
    responses={
        200: OpenApiResponse(description="Script outline retrieved successfully"),
        404: OpenApiResponse(description="Script outline not found")
    }
)
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
    summary="Generate full script",
    description="Generate a complete script from an existing outline using OpenAI",
    responses={
        201: OpenApiResponse(description="Full script generated successfully"),
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


@extend_schema(
    summary="Get full script",
    description="Retrieve a specific full script by its UUID",
    responses={
        200: OpenApiResponse(description="Full script retrieved successfully"),
        404: OpenApiResponse(description="Full script not found")
    }
)
class FullScriptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Full CRUD for full scripts
    """
    queryset = FullScript.objects.select_related('outline', 'outline__script')
    serializer_class = FullScriptSerializer
    lookup_field = 'uuid'


@extend_schema(
    summary="List all script outlines",
    description="Retrieve a paginated list of all script outlines",
    responses={
        200: OpenApiResponse(description="Script outlines retrieved successfully")
    }
)
class ScriptOutlineListView(generics.ListAPIView):
    """
    List all script outlines
    """
    serializer_class = ScriptOutlineSerializer

    def get_queryset(self):
        return ScriptOutline.objects.select_related(
            'script', 'script__tone'
        ).order_by('-created')


@extend_schema(
    summary="List all full scripts",
    description="Retrieve a paginated list of all full scripts",
    responses={
        200: OpenApiResponse(description="Full scripts retrieved successfully")
    }
)
class FullScriptListView(generics.ListAPIView):
    """
    List all full scripts
    """
    serializer_class = FullScriptSerializer

    def get_queryset(self):
        return FullScript.objects.select_related(
            'outline', 'outline__script'
        ).order_by('-created')