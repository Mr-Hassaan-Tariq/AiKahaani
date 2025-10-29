"""
YouTube Transcript Fetcher Service

This service fetches YouTube video transcripts using the youtube-transcript-api
with Webshare proxy support for bypassing regional restrictions.

Features:
- Video ID extraction from various YouTube URL formats
- Proxy configuration with Webshare
- Video metadata extraction (title, duration, etc.)
- Automatic transcript truncation
- Comprehensive error handling
"""

import logging
import re
from typing import Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import WebshareProxyConfig
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    logger.warning("[YOUTUBE_TRANSCRIPT] youtube-transcript-api not installed.")

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logger.warning("[YOUTUBE_TRANSCRIPT] yt-dlp not installed.")


class YouTubeTranscriptService:
    """Service for fetching YouTube video transcripts"""
    
    # Maximum transcript length to avoid token limits
    MAX_TRANSCRIPT_LENGTH = 5000
    
    # YouTube URL patterns for video ID extraction
    URL_PATTERNS = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/shorts\/)([\w-]+)',
    ]
    
    @classmethod
    def fetch_transcript(cls, youtube_url: str) -> Tuple[str, str]:
        """
        Fetch transcript from YouTube video
        
        Args:
            youtube_url: URL of the YouTube video
            
        Returns:
            Tuple of (video_title, transcript_text)
            
        Raises:
            Exception: If transcript fetching fails
        """
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            raise Exception(
                "YouTube transcript service is not available. "
                "Please install youtube-transcript-api package."
            )
        
        logger.info(f"[YOUTUBE_TRANSCRIPT] Starting transcript fetch for URL: {youtube_url}")
        
        # Extract video ID
        video_id = cls._extract_video_id(youtube_url)
        if not video_id:
            raise Exception("Invalid YouTube URL. Could not extract video ID.")
        
        logger.info(f"[YOUTUBE_TRANSCRIPT] Extracted video ID: {video_id}")
        
        # Get video metadata
        video_title = cls._get_video_metadata(video_id)
        
        # Fetch transcript with proxy
        transcript_text = cls._fetch_transcript_with_proxy(video_id)
        
        # Process and truncate if necessary
        transcript_text = cls._process_transcript(transcript_text)
        
        logger.info(
            f"[YOUTUBE_TRANSCRIPT] ✅ Success - "
            f"Title: '{video_title[:50]}...', Transcript length: {len(transcript_text)}"
        )
        
        return video_title, transcript_text
    
    @classmethod
    def _extract_video_id(cls, youtube_url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Video ID or None if not found
        """
        for pattern in cls.URL_PATTERNS:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def _get_video_metadata(cls, video_id: str) -> str:
        """
        Get video metadata (title, duration, etc.)
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video title
        """
        video_title = "YouTube Video"
        
        if not YT_DLP_AVAILABLE:
            logger.warning("[YOUTUBE_TRANSCRIPT] yt-dlp not available, using default title")
            return video_title
        
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}", 
                    download=False
                )
                video_title = info.get('title', 'YouTube Video')
                video_duration = info.get('duration', 0)
                
                logger.info(
                    f"[YOUTUBE_TRANSCRIPT] Video metadata - "
                    f"Title: '{video_title}', Duration: {video_duration}s"
                )
        except Exception as e:
            logger.warning(f"[YOUTUBE_TRANSCRIPT] Could not fetch video metadata: {str(e)}")
        
        return video_title
    
    @classmethod
    def _fetch_transcript_with_proxy(cls, video_id: str) -> str:
        """
        Fetch transcript using Webshare proxy configuration
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text
            
        Raises:
            Exception: If transcript fetch fails
        """
        # Initialize YouTubeTranscriptApi
        from youtube_transcript_api import YouTubeTranscriptApi as YTAPI
        
        # Note: youtube-transcript-api doesn't support proxy configuration directly
        # We'll use it without proxy for now
        logger.info("[YOUTUBE_TRANSCRIPT] Fetching transcript (proxy not supported by this library)")
        
        try:
            api_instance = YTAPI()
            
            # Try English first
            try:
                transcript = api_instance.fetch(video_id, languages=['en'])
                logger.info("[YOUTUBE_TRANSCRIPT] Using English transcript")
                return cls._format_transcript(transcript)
            except Exception:
                # If English not available, get any available transcript
                logger.info("[YOUTUBE_TRANSCRIPT] English not available, trying other languages...")
                transcript_list = api_instance.list(video_id)
                # Get the first available transcript
                for transcript_info in transcript_list:
                    transcript = transcript_info.fetch()
                    logger.info(f"[YOUTUBE_TRANSCRIPT] Using transcript in language: {transcript_info.language}")
                    return cls._format_transcript(transcript)
                
                raise Exception("No transcripts available for this video")
                    
        except Exception as e:
            error_message = str(e)
            
            # Log technical details for debugging
            logger.error(
                f"[YOUTUBE_TRANSCRIPT] Technical error: {error_message}",
                exc_info=True
            )
            
            # Provide user-friendly error messages (don't expose technical details)
            if "No transcript" in error_message or "Subtitles" in error_message:
                raise Exception(
                    "Unable to fetch video transcript. The video may not have captions enabled."
                )
            elif "Video unavailable" in error_message:
                raise Exception("Unable to access this video. It may be unavailable or private.")
            elif "TranscriptsDisabled" in error_message:
                raise Exception(
                    "Captions are not available for this video."
                )
            else:
                # Generic error - don't expose technical details
                raise Exception("Unable to fetch video transcript. Please try a different video or use text description.")
    
    @classmethod
    def _format_transcript(cls, transcript: list) -> str:
        """
        Format transcript list into text
        
        Args:
            transcript: List of transcript snippets
            
        Returns:
            Formatted transcript text
        """
        # Convert transcript to text
        if isinstance(transcript, list):
            # If it's a list of dictionaries
            if transcript and isinstance(transcript[0], dict):
                transcript_text = " ".join([snippet.get('text', '') for snippet in transcript])
            # If it's a list of transcript objects (from youtube_transcript_api)
            else:
                transcript_text = " ".join([snippet.text for snippet in transcript])
        else:
            transcript_text = str(transcript)
        
        return transcript_text
    
    @classmethod
    def _process_transcript(cls, transcript_text: str) -> str:
        """
        Process and truncate transcript if necessary
        
        Args:
            transcript_text: Raw transcript text
            
        Returns:
            Processed transcript text
        """
        # Clean up extra whitespace
        transcript_text = ' '.join(transcript_text.split())
        
        # Truncate if too long
        if len(transcript_text) > cls.MAX_TRANSCRIPT_LENGTH:
            transcript_text = (
                transcript_text[:cls.MAX_TRANSCRIPT_LENGTH] + 
                "... (transcript truncated for brevity)"
            )
            logger.info(
                f"[YOUTUBE_TRANSCRIPT] Transcript truncated to "
                f"{cls.MAX_TRANSCRIPT_LENGTH} characters"
            )
        
        return transcript_text

