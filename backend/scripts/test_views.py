"""
Test Views for Attachment Features

These endpoints test each attachment type individually:
- Image analysis (file/URL)
- Article scraping
- YouTube transcript fetching

Use these to verify each service works before testing combined functionality.
"""

import logging
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.core.files.uploadedfile import UploadedFile

from scripts.services.open_ai import OpenAIScriptService

logger = logging.getLogger(__name__)


@extend_schema(
    summary="Test Image Analysis",
    description="""Test image analysis functionality independently.
    
Supports both file upload and URL input.

**Usage:**
- For file: Use multipart/form-data with 'image' field
- For URL: Use JSON with 'image_url' field

Returns the AI-generated title and description of the image.""",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "format": "binary"}
            }
        },
        "application/json": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "format": "uri"}
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="Image analyzed successfully",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "message": {"type": "string"}
                }
            }
        ),
        400: OpenApiResponse(description="Invalid input - image or image_url required"),
        500: OpenApiResponse(description="Image analysis failed"),
    },
    examples=[
        OpenApiExample(
            "Image Upload",
            value={"image": "[Upload file]"},
            request_only=True,
        ),
        OpenApiExample(
            "Image URL",
            value={"image_url": "https://example.com/image.jpg"},
            request_only=True,
        ),
    ],
    tags=["Testing"]
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated])
def test_image_analysis(request):
    """Test image analysis independently"""
    logger.info(f"[TEST_IMAGE] Request from user {request.user.id}")
    
    image = request.FILES.get("image") or request.data.get("image")
    image_url = request.data.get("image_url", "").strip()
    
    # Validate input
    if not image and not image_url:
        logger.warning(f"[TEST_IMAGE] Missing input from user {request.user.id}")
        return Response(
            {
                "success": False,
                "error": "Either 'image' file or 'image_url' must be provided."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if image and image_url:
        logger.warning(f"[TEST_IMAGE] Both inputs provided from user {request.user.id}")
        return Response(
            {
                "success": False,
                "error": "Provide either image file or URL, not both."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Test image analysis
        if image:
            if hasattr(image, "read") and hasattr(image, "seek"):
                logger.info(f"[TEST_IMAGE] Testing with uploaded file from user {request.user.id}")
                title, description = OpenAIScriptService.analyze_image_with_assistant(
                    image_file=image,
                    user=request.user
                )
            else:
                return Response(
                    {
                        "success": False,
                        "error": "Invalid image file."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            logger.info(f"[TEST_IMAGE] Testing with URL from user {request.user.id}: {image_url}")
            title, description = OpenAIScriptService.analyze_image_with_assistant(
                image_url=image_url,
                user=request.user
            )
        
        logger.info(
            f"[TEST_IMAGE] ✅ Success for user {request.user.id} - "
            f"Title: '{title[:50]}...', Description length: {len(description)}"
        )
        
        return Response(
            {
                "success": True,
                "title": title,
                "description": description,
                "message": "Image analyzed successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"[TEST_IMAGE] ❌ Failed for user {request.user.id}: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": f"Image analysis failed: {str(e)}"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Test Article Scraping",
    description="""Test article content scraping functionality independently.

Scrapes article content from the provided URL using multiple fallback methods.

**Returns:**
- Article title
- Scraped content (truncated to 3000 chars)

**Note:** Some sites may block scraping or require JavaScript.""",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "article_url": {
                    "type": "string",
                    "format": "uri",
                    "description": "URL of the article to scrape"
                }
            },
            "required": ["article_url"]
        }
    },
    responses={
        200: OpenApiResponse(
            description="Article scraped successfully",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "content_length": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        ),
        400: OpenApiResponse(description="Invalid input - article_url required"),
        500: OpenApiResponse(description="Article scraping failed"),
    },
    examples=[
        OpenApiExample(
            "BBC News Article",
            value={"article_url": "https://www.bbc.com/news/technology-123456"},
        ),
        OpenApiExample(
            "Medium Blog Post",
            value={"article_url": "https://medium.com/@author/article-title"},
        ),
    ],
    tags=["Testing"]
)
@api_view(["POST"])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def test_article_scraping(request):
    """Test article scraping independently"""
    logger.info(f"[TEST_ARTICLE] Request from user {request.user.id}")
    
    article_url = request.data.get("article_url", "").strip()
    
    # Validate input
    if not article_url:
        logger.warning(f"[TEST_ARTICLE] Missing URL from user {request.user.id}")
        return Response(
            {
                "success": False,
                "error": "The 'article_url' field is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Test article scraping
        logger.info(f"[TEST_ARTICLE] Testing scraping from user {request.user.id}: {article_url}")
        title, content = OpenAIScriptService.analyze_article_content(
            article_url=article_url,
            user=request.user
        )
        
        logger.info(
            f"[TEST_ARTICLE] ✅ Success for user {request.user.id} - "
            f"Title: '{title[:50]}...', Content length: {len(content)}"
        )
        
        return Response(
            {
                "success": True,
                "title": title,
                "content": content,
                "content_length": len(content),
                "message": "Article scraped successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"[TEST_ARTICLE] ❌ Failed for user {request.user.id}: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": f"Article scraping failed: {str(e)}"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Test YouTube Transcript",
    description="""Test YouTube transcript fetching functionality independently.

Fetches transcript from the provided YouTube video URL using Webshare proxy.

**Returns:**
- Video title
- Transcript text (truncated to 5000 chars)

**Supported URL formats:**
- youtube.com/watch?v=VIDEO_ID
- youtu.be/VIDEO_ID
- youtube.com/embed/VIDEO_ID
- youtube.com/shorts/VIDEO_ID

**Note:** Video must have captions/subtitles enabled.""",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "youtube_url": {
                    "type": "string",
                    "format": "uri",
                    "description": "URL of the YouTube video"
                }
            },
            "required": ["youtube_url"]
        }
    },
    responses={
        200: OpenApiResponse(
            description="Transcript fetched successfully",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "video_title": {"type": "string"},
                    "transcript": {"type": "string"},
                    "transcript_length": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        ),
        400: OpenApiResponse(description="Invalid input - youtube_url required"),
        500: OpenApiResponse(description="Transcript fetching failed"),
    },
    examples=[
        OpenApiExample(
            "Standard YouTube Video",
            value={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        ),
        OpenApiExample(
            "YouTube Short URL",
            value={"youtube_url": "https://youtu.be/dQw4w9WgXcQ"},
        ),
        OpenApiExample(
            "YouTube Shorts",
            value={"youtube_url": "https://www.youtube.com/shorts/abc123"},
        ),
    ],
    tags=["Testing"]
)
@api_view(["POST"])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def test_youtube_transcript(request):
    """Test YouTube transcript fetching independently"""
    logger.info(f"[TEST_YOUTUBE] Request from user {request.user.id}")
    
    youtube_url = request.data.get("youtube_url", "").strip()
    
    # Validate input
    if not youtube_url:
        logger.warning(f"[TEST_YOUTUBE] Missing URL from user {request.user.id}")
        return Response(
            {
                "success": False,
                "error": "The 'youtube_url' field is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Test YouTube transcript fetching
        logger.info(f"[TEST_YOUTUBE] Testing transcript from user {request.user.id}: {youtube_url}")
        video_title, transcript = OpenAIScriptService.analyze_youtube_transcript(
            youtube_url=youtube_url,
            user=request.user
        )
        
        logger.info(
            f"[TEST_YOUTUBE] ✅ Success for user {request.user.id} - "
            f"Title: '{video_title[:50]}...', Transcript length: {len(transcript)}"
        )
        
        return Response(
            {
                "success": True,
                "video_title": video_title,
                "transcript": transcript,
                "transcript_length": len(transcript),
                "message": "Transcript fetched successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"[TEST_YOUTUBE] ❌ Failed for user {request.user.id}: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": f"Transcript fetching failed: {str(e)}"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Test All Attachments Combined",
    description="""Test all attachment types together to see how they combine.

Processes image, article, and YouTube transcript, then shows how the contexts are combined.

**All fields are optional** - provide any combination to test.

**Returns:**
- Individual contexts from each attachment
- Combined context showing how they're merged
- Total combined length

This endpoint helps verify context combination logic.""",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "format": "binary"},
                "image_url": {"type": "string", "format": "uri"},
                "article_url": {"type": "string", "format": "uri"},
                "youtube_url": {"type": "string", "format": "uri"}
            }
        },
        "application/json": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "format": "uri"},
                "article_url": {"type": "string", "format": "uri"},
                "youtube_url": {"type": "string", "format": "uri"}
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description="Attachments processed successfully",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "attachments_processed": {"type": "integer"},
                    "contexts": {"type": "object"},
                    "combined_context": {"type": "string"},
                    "combined_length": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        ),
        400: OpenApiResponse(description="No attachments provided"),
        500: OpenApiResponse(description="Processing failed"),
    },
    examples=[
        OpenApiExample(
            "All Attachments",
            value={
                "image_url": "https://example.com/image.jpg",
                "article_url": "https://www.bbc.com/news/technology-123",
                "youtube_url": "https://www.youtube.com/watch?v=abc123"
            },
        ),
        OpenApiExample(
            "Image + Article",
            value={
                "image_url": "https://example.com/photo.jpg",
                "article_url": "https://medium.com/@author/post"
            },
        ),
    ],
    tags=["Testing"]
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([IsAuthenticated])
def test_combined_attachments(request):
    """Test all attachment types combined"""
    logger.info(f"[TEST_COMBINED] Request from user {request.user.id}")
    
    image = request.FILES.get("image") or request.data.get("image")
    image_url = request.data.get("image_url", "").strip()
    article_url = request.data.get("article_url", "").strip()
    youtube_url = request.data.get("youtube_url", "").strip()
    
    # Check if at least one attachment provided
    if not any([image, image_url, article_url, youtube_url]):
        logger.warning(f"[TEST_COMBINED] No attachments from user {request.user.id}")
        return Response(
            {
                "success": False,
                "error": "At least one attachment must be provided (image, image_url, article_url, or youtube_url)."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check image conflict
    if image and image_url:
        return Response(
            {
                "success": False,
                "error": "Provide either image file or URL, not both."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    contexts = {}
    additional_contexts = []
    errors = []
    
    # Process Image
    if image or image_url:
        try:
            logger.info(f"[TEST_COMBINED] Processing image for user {request.user.id}")
            if image and hasattr(image, "read") and hasattr(image, "seek"):
                title, description = OpenAIScriptService.analyze_image_with_assistant(
                    image_file=image,
                    user=request.user
                )
            elif image_url:
                title, description = OpenAIScriptService.analyze_image_with_assistant(
                    image_url=image_url,
                    user=request.user
                )
            else:
                raise ValueError("Invalid image file")
            
            contexts["image"] = {"title": title, "description": description}
            additional_contexts.append(f"[IMAGE CONTEXT]: {description}")
            logger.info(f"[TEST_COMBINED] ✅ Image processed for user {request.user.id}")
        except Exception as e:
            error_msg = f"Image processing failed: {str(e)}"
            errors.append(error_msg)
            logger.error(f"[TEST_COMBINED] ❌ Image error for user {request.user.id}: {str(e)}")
    
    # Process Article
    if article_url:
        try:
            logger.info(f"[TEST_COMBINED] Processing article for user {request.user.id}")
            title, content = OpenAIScriptService.analyze_article_content(
                article_url=article_url,
                user=request.user
            )
            contexts["article"] = {"title": title, "content": content}
            additional_contexts.append(f"[ARTICLE CONTEXT - {title}]: {content}")
            logger.info(f"[TEST_COMBINED] ✅ Article processed for user {request.user.id}")
        except Exception as e:
            error_msg = f"Article scraping failed: {str(e)}"
            errors.append(error_msg)
            logger.error(f"[TEST_COMBINED] ❌ Article error for user {request.user.id}: {str(e)}")
    
    # Process YouTube
    if youtube_url:
        try:
            logger.info(f"[TEST_COMBINED] Processing YouTube for user {request.user.id}")
            video_title, transcript = OpenAIScriptService.analyze_youtube_transcript(
                youtube_url=youtube_url,
                user=request.user
            )
            contexts["youtube"] = {"title": video_title, "transcript": transcript}
            additional_contexts.append(f"[YOUTUBE TRANSCRIPT - {video_title}]: {transcript}")
            logger.info(f"[TEST_COMBINED] ✅ YouTube processed for user {request.user.id}")
        except Exception as e:
            error_msg = f"YouTube transcript failed: {str(e)}"
            errors.append(error_msg)
            logger.error(f"[TEST_COMBINED] ❌ YouTube error for user {request.user.id}: {str(e)}")
    
    # Check if any succeeded
    if not additional_contexts:
        logger.error(f"[TEST_COMBINED] All attachments failed for user {request.user.id}")
        return Response(
            {
                "success": False,
                "errors": errors,
                "message": "All attachment processing failed"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Combine contexts
    combined_context = "\n\n".join(additional_contexts)
    
    logger.info(
        f"[TEST_COMBINED] ✅ Success for user {request.user.id} - "
        f"Processed {len(additional_contexts)} attachment(s), Combined length: {len(combined_context)}"
    )
    
    return Response(
        {
            "success": True,
            "attachments_processed": len(additional_contexts),
            "contexts": contexts,
            "combined_context": combined_context,
            "combined_length": len(combined_context),
            "errors": errors if errors else None,
            "message": f"Processed {len(additional_contexts)} attachment(s) successfully"
        },
        status=status.HTTP_200_OK
    )

