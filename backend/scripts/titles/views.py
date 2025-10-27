# titles/views.py
import logging

from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    OpenApiParameter
)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination


from api.mixins import MethodSpecificThrottleMixin
from notifications.helpers import NotificationHelper
from payments.permissions import HasActiveSubscriptionPermission
from scripts.models import ScriptTitle, TitleTone, UserTitles
from scripts.services.open_ai import OpenAIScriptService

from .serializers import (
    GenerateTitlesOptimizedRequestSerializer,
    GenerateTitlesRequestSerializer,
    GenerateTitlesResponseSerializer,
    TitleToneSerializer,
)
from scripts.utils import save_generated_titles

logger = logging.getLogger(__name__)


class GenerateTitlesView(APIView, MethodSpecificThrottleMixin):
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    @extend_schema(
        summary="Generate YouTube titles",
        description="Generate engaging YouTube titles based on TubeGenius Title Wizardry principles",
        request=GenerateTitlesRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=GenerateTitlesResponseSerializer,
                description="Titles generated successfully",
            ),
            429: OpenApiResponse(description="Rate limit exceeded"),
            500: OpenApiResponse(description="Title generation failed"),
        },
    )
    def post(self, request):
        """
        Generate YouTube titles based on input prompt

        Tone Validation Rules:
        - Maximum 3 tones allowed
        - Contradicting combinations are prevented (e.g., Neutral + Controversial)
        - Too many intense tones (3+ of: Controversial, Shocking, Dramatic) are blocked
        - Some style conflicts are detected (e.g., Question-based + Sarcastic)
        """
        # Validate input
        serializer = GenerateTitlesRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        prompt = validated_data["prompt"]
        title_count = validated_data["title_count"]
        tones = validated_data.get("tones", [])
        titles, metadata = OpenAIScriptService.generate_titles(
            prompt=prompt, title_count=title_count, tones=tones, user=request.user
        )

        # Prepare response - extract title strings from title objects
        title_strings = [
            title.get("title", "") for title in titles if isinstance(title, dict)
        ]
        tone_message = f" with tones: {', '.join(tones)}" if tones else ""
        response_data = {
            "titles": title_strings,
            "metadata": metadata,
            "message": f"Successfully generated {len(title_strings)} YouTube titles{tone_message}",
        }

        # Validate response
        response_serializer = GenerateTitlesResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            ScriptTitle.objects.create(
                user=request.user,
                titles=title_strings,
                titles_count=len(title_strings),
                prompt=prompt,
            )

            # ✅ Save in UserTitles model (append unique titles)
            save_generated_titles(
                user=request.user,
                titles=title_strings,
                prompt=prompt,
                tones=tones
            )

            # Create notification for successful title generation
            try:
                NotificationHelper.create_user_notification(
                    user=request.user,
                    title="🎬 Titles Generated Successfully!",
                    message=f"Your {len(titles)} YouTube titles have been generated and are ready for review. Check them out in your dashboard!",
                    notification_type="title",
                )
            except Exception as e:
                logger.warning(
                    f"Failed to create title generation notification: {str(e)}"
                )

            return Response(
                response_serializer.validated_data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to format response"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerateTitlesOptimizedView(APIView, MethodSpecificThrottleMixin):
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]

    @extend_schema(
        summary="Generate optimized YouTube titles",
        description="Generate optimized YouTube titles from existing script content or user-provided title",
        request=GenerateTitlesOptimizedRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=GenerateTitlesResponseSerializer,
                description="Optimized titles generated successfully",
            ),
            400: OpenApiResponse(description="Invalid request data"),
            404: OpenApiResponse(description="Script not found or access denied"),
            429: OpenApiResponse(description="Rate limit exceeded"),
            500: OpenApiResponse(description="Title optimization failed"),
        },
    )
    def post(self, request):
        """
        Generate optimized YouTube titles

        Two modes of operation:
        1. Script-based: Provide script UUID - uses script content + user prompt
        2. Title-based: Provide user_title + prompt for optimization

        Features:
        - Validates script ownership for authenticated users
        - Combines script content with user prompt for context
        - Supports tone customization with validation
        - Returns same format as GenerateTitlesView
        """
        # Validate input
        serializer = GenerateTitlesOptimizedRequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        script = validated_data.get(
            "script"
        )  # This is now a Script object from validation
        user_title = validated_data.get("user_title")
        user_prompt = validated_data["prompt"]
        title_count = validated_data["title_count"]
        tones = validated_data.get("tones", [])

        try:
            # Generate optimized titles using the OpenAI service
            titles, metadata = OpenAIScriptService.generate_optimized_titles(
                script=script,
                user_title=user_title,
                user_prompt=user_prompt,
                title_count=title_count,
                tones=tones,
                user=request.user,
            )

            # Prepare response - extract title strings from title objects
            title_strings = [
                title.get("title", "") for title in titles if isinstance(title, dict)
            ]
            tone_message = f" with tones: {', '.join(tones)}" if tones else ""
            response_data = {
                "titles": title_strings,
                "metadata": metadata,
                "message": f"Successfully generated {len(title_strings)} optimized YouTube titles{tone_message}",
            }

            # Validate response
            response_serializer = GenerateTitlesResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                # Create ScriptTitle record with optimization flag
                # Logic: If script provided -> use script reference, no user_provided_title
                #        If no script -> no script reference, but store user_provided_title
                if script:
                    # Script-based optimization
                    ScriptTitle.objects.create(
                        user=request.user,
                        script=script,  # Use the script object directly
                        is_optimized_title=True,
                        titles=title_strings,
                        titles_count=len(title_strings),
                        prompt=user_prompt,
                        user_provided_title=None,  # Don't store user title when script is provided
                    )
                else:
                    # Title-based optimization
                    ScriptTitle.objects.create(
                        user=request.user,
                        script=None,  # No script reference
                        is_optimized_title=True,
                        titles=title_strings,
                        titles_count=len(title_strings),
                        prompt=user_prompt,
                        user_provided_title=user_title,  # Store the user provided title
                    )

                # ✅ Save unique titles to UserTitles model
                save_generated_titles(
                    user=request.user,
                    titles=title_strings,
                    prompt=user_prompt,
                    tones=tones,
                    user_title=user_title,
                    script=script
                )

                # Create notification for successful optimized title generation
                try:
                    optimization_type = "script-based" if script else "title-based"
                    NotificationHelper.create_user_notification(
                        user=request.user,
                        title="✨ Titles Optimized Successfully!",
                        message=f"Your {len(titles)} optimized YouTube titles have been generated using {optimization_type} optimization. Check them out in your dashboard!",
                        notification_type="title",
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to create optimized title notification: {str(e)}"
                    )

                return Response(
                    response_serializer.validated_data, status=status.HTTP_200_OK
                )
            else:
                logger.error(
                    f"Response serialization failed: {response_serializer.errors}"
                )
                return Response(
                    {"error": "Failed to format response"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            logger.error(f"Title optimization failed: {str(e)}")
            return Response(
                {"error": "Title optimization failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TitleToneListView(generics.ListAPIView, MethodSpecificThrottleMixin):
    """
    List all available title tones for use in title generation
    """

    queryset = TitleTone.objects.all()
    serializer_class = TitleToneSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all available title tones",
        description="Get a list of all available tones that can be used for title generation",
        responses={
            200: OpenApiResponse(
                response=TitleToneSerializer(many=True),
                description="List of available title tones",
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserTitlesListView(APIView, LimitOffsetPagination):
    permission_classes = [IsAuthenticated, HasActiveSubscriptionPermission]
    default_limit = 10  # optional default page size

    @extend_schema(
        summary="Get all saved titles, tones, and prompts for the authenticated user (paginated)",
        description=(
            "Retrieve a paginated list of unique titles, tones, and prompts generated or optimized "
            "by the authenticated user. Each record represents one saved UserTitles entry."
        ),
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Number of results to return per page.",
                examples=[{"value": 10}],
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="The initial index from which to return results.",
                examples=[{"value": 0}],
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Paginated list of titles, tones, and prompts retrieved successfully",
                response={
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "example": 23},
                        "next": {
                            "type": ["string", "null"],
                            "example": "https://api.example.com/api/user-titles/?limit=10&offset=10"
                        },
                        "previous": {
                            "type": ["string", "null"],
                            "example": None
                        },
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "user": {"type": "string", "example": "john_doe"},
                                    "titles": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "example": [
                                            "How to Grow on YouTube Fast",
                                            "10 Tips for Better Thumbnails"
                                        ],
                                    },
                                    "tones": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "example": ["Professional", "Funny"],
                                    },
                                    "prompts": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "example": [
                                            "Generate a YouTube title for a travel vlog",
                                            "Optimize my video title for engagement"
                                        ],
                                    },
                                },
                            },
                        },
                    },
                },
            ),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
        },
    )
    def get(self, request):
        """
        Retrieve paginated titles, tones, and prompts for the authenticated user.
        Each result represents one UserTitles record.
        """
        user = request.user
        user_titles_qs = UserTitles.objects.filter(user=user)

        # Transform queryset into serializable list
        data = []
        for record in user_titles_qs:
            data.append({
                "user": user.username,
                "titles": record.titles or [],
                "tones": getattr(record, "tones", []) or [],
                "prompts": getattr(record, "prompts", []) or [],
            })

        # Apply pagination
        paginated_results = self.paginate_queryset(data, request, view=self)
        return self.get_paginated_response(paginated_results)
