"""
YouTube Transcript Fetcher Service (async)

Fetches transcripts using youtube-transcript-api + yt-dlp for metadata.
No Django dependency — uses settings from app.config.
"""

import asyncio
import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    logger.warning("[YOUTUBE_TRANSCRIPT] youtube-transcript-api not installed")

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

MAX_TRANSCRIPT_LENGTH = 5000
URL_PATTERN = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/"
    r"|youtube\.com/v/|youtube\.com/shorts/)([\w-]+)"
)


async def fetch_transcript(youtube_url: str) -> Tuple[str, str]:
    """
    Fetch transcript from YouTube video. Returns (video_title, transcript_text).
    Raises Exception if fetching fails.
    """
    if not TRANSCRIPT_AVAILABLE:
        raise Exception("YouTube transcript service unavailable (package not installed).")

    video_id = _extract_video_id(youtube_url)
    if not video_id:
        raise Exception("Invalid YouTube URL — could not extract video ID.")

    # Metadata fetch is sync (yt-dlp), run in executor
    video_title = await asyncio.get_event_loop().run_in_executor(
        None, _get_video_title, video_id
    )

    # Transcript fetch is sync, run in executor
    transcript_text = await asyncio.get_event_loop().run_in_executor(
        None, _fetch_transcript_sync, video_id
    )

    transcript_text = _process_transcript(transcript_text)
    logger.info(
        "[YOUTUBE_TRANSCRIPT] Success — title: '%s...', length: %d",
        video_title[:50],
        len(transcript_text),
    )
    return video_title, transcript_text


def _extract_video_id(url: str) -> Optional[str]:
    match = URL_PATTERN.search(url)
    return match.group(1) if match else None


def _get_video_title(video_id: str) -> str:
    if not YT_DLP_AVAILABLE:
        return "YouTube Video"
    try:
        opts = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
            return info.get("title", "YouTube Video")
    except Exception as exc:
        logger.warning("[YOUTUBE_TRANSCRIPT] Metadata fetch failed: %s", exc)
        return "YouTube Video"


def _fetch_transcript_sync(video_id: str) -> str:
    try:
        api = YouTubeTranscriptApi()
        try:
            snippet_list = api.fetch(video_id, languages=["en"])
            return _format_transcript(snippet_list)
        except Exception:
            transcript_list = api.list(video_id)
            for t in transcript_list:
                return _format_transcript(t.fetch())
            raise Exception("No transcripts available for this video.")
    except Exception as exc:
        err = str(exc)
        logger.error("[YOUTUBE_TRANSCRIPT] Fetch failed: %s", err)
        if "No transcript" in err or "Subtitles" in err:
            raise Exception("Video has no captions enabled.")
        elif "Video unavailable" in err:
            raise Exception("Video is unavailable or private.")
        elif "TranscriptsDisabled" in err:
            raise Exception("Captions are disabled for this video.")
        raise Exception(
            "Unable to fetch video transcript. Try a different video or use text description."
        )


def _format_transcript(transcript) -> str:
    if isinstance(transcript, list):
        if transcript and isinstance(transcript[0], dict):
            return " ".join(s.get("text", "") for s in transcript)
        return " ".join(s.text for s in transcript)
    return str(transcript)


def _process_transcript(text: str) -> str:
    text = " ".join(text.split())
    if len(text) > MAX_TRANSCRIPT_LENGTH:
        text = text[:MAX_TRANSCRIPT_LENGTH] + "... (transcript truncated)"
    return text
