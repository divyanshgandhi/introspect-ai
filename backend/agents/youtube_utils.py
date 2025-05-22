"""
YouTube utilities for transcript extraction and content processing.
This module provides backup functionality when the primary Agno YouTube tools fail.
"""

import logging
import re
import requests
from typing import Optional, Dict, List, Any, Union, Tuple

logger = logging.getLogger("introspect_agent")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )

    YOUTUBE_TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    logger.warning(
        "youtube_transcript_api not installed. Using fallback mechanisms only."
    )
    YOUTUBE_TRANSCRIPT_API_AVAILABLE = False
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception
    VideoUnavailable = Exception


def extract_video_id(youtube_url: str) -> Optional[str]:
    """
    Extract the video ID from a YouTube URL.

    Args:
        youtube_url: The YouTube URL

    Returns:
        The video ID or None if not found
    """
    if not youtube_url:
        return None

    # Common YouTube URL patterns
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standard and shortened URLs
        r"(?:embed\/)([0-9A-Za-z_-]{11})",  # Embedded videos
        r"(?:watch\?v=)([0-9A-Za-z_-]{11})",  # Standard watch URLs
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",  # Short URLs
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    logger.warning(f"Could not extract video ID from URL: {youtube_url}")
    return None


def get_video_info(video_id: str) -> Dict[str, Any]:
    """
    Fetch basic information about a YouTube video.

    Args:
        video_id: The YouTube video ID

    Returns:
        Dictionary containing video information
    """
    default_info = {"title": "Unknown YouTube Video", "author_name": "Unknown"}

    if not video_id:
        logger.warning("Cannot get video info: No video ID provided")
        return default_info

    try:
        # Use the oEmbed API to get basic video information
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        logger.debug(f"Fetching video info from: {oembed_url}")

        response = requests.get(oembed_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Successfully retrieved video info for {video_id}")
            return data
        else:
            logger.warning(
                f"Failed to get video info for {video_id}. Status code: {response.status_code}"
            )
            return default_info
    except Exception as e:
        logger.exception(f"Error fetching video info: {str(e)}")
        return default_info


def get_transcript(youtube_url: str) -> Optional[str]:
    """
    Get the transcript for a YouTube video.

    Args:
        youtube_url: The URL of the YouTube video

    Returns:
        The video transcript as a string, or None if no transcript is available
    """
    video_id = extract_video_id(youtube_url)
    if not video_id:
        logger.error(f"Could not extract video ID from URL: {youtube_url}")
        return None

    # Try to get transcript using youtube_transcript_api if available
    if YOUTUBE_TRANSCRIPT_API_AVAILABLE:
        try:
            logger.debug(f"Attempting to get transcript for video {video_id}")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            if not transcript_list:
                logger.warning(f"Empty transcript list returned for video {video_id}")
                return None

            # Combine all transcript pieces into a single string
            transcript_text = " ".join(
                [item.get("text", "") for item in transcript_list if item.get("text")]
            )

            if not transcript_text.strip():
                logger.warning(f"Empty transcript text for video {video_id}")
                return None

            # Get video info for context
            video_info = get_video_info(video_id)

            # Create a formatted transcript with video title and content
            formatted_transcript = f"Title: {video_info.get('title', 'Unknown')}\n"
            formatted_transcript += (
                f"Channel: {video_info.get('author_name', 'Unknown')}\n\n"
            )
            formatted_transcript += f"Transcript:\n{transcript_text}"

            logger.debug(
                f"Successfully retrieved transcript for video {video_id} ({len(transcript_text)} chars)"
            )
            return formatted_transcript

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"No transcript available for video {video_id}: {str(e)}")
        except VideoUnavailable:
            logger.warning(f"Video {video_id} is unavailable")
        except Exception as e:
            logger.exception(f"Error fetching transcript for {video_id}: {str(e)}")

    # If we reach here, we couldn't get the transcript
    return None


def validate_youtube_content(content: Optional[str]) -> Tuple[bool, str]:
    """
    Validate YouTube content to ensure it's usable.

    Args:
        content: The content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if content is None:
        return False, "Content is None"

    if not isinstance(content, str):
        return False, f"Content is not a string (type: {type(content)})"

    if not content.strip():
        return False, "Content is empty or whitespace only"

    min_content_length = 50  # Arbitrary minimum for a useful transcript
    if len(content) < min_content_length:
        return (
            False,
            f"Content is too short ({len(content)} chars, minimum {min_content_length})",
        )

    return True, ""


def process_youtube_content(youtube_url: str) -> Dict[str, Any]:
    """
    Process YouTube content to extract key information.

    Args:
        youtube_url: The URL of the YouTube video

    Returns:
        Dictionary with video info and transcript
    """
    logger.info(f"Processing YouTube content from: {youtube_url}")

    video_id = extract_video_id(youtube_url)
    if not video_id:
        logger.error(f"Invalid YouTube URL: {youtube_url}")
        return {"error": True, "message": "Invalid YouTube URL", "content": None}

    # Get video information
    video_info = get_video_info(video_id)
    logger.debug(f"Video info retrieved: {video_info.get('title', 'Unknown')}")

    # Get transcript
    transcript = get_transcript(youtube_url)

    # Validate transcript
    is_valid, error_message = validate_youtube_content(transcript)
    if not is_valid:
        logger.error(f"Invalid transcript: {error_message}")
        return {
            "error": True,
            "message": f"Could not retrieve valid transcript: {error_message}",
            "video_info": video_info,
            "content": None,
        }

    logger.info(
        f"Successfully processed YouTube content for video: {video_info.get('title', 'Unknown')}"
    )
    return {"error": False, "video_info": video_info, "content": transcript}
