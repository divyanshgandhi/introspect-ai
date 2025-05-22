"""
Test script for YouTube transcript extraction

This script tests both the backup YouTube transcript extraction and the full agent extraction
pipeline, helping identify issues with event loops and NoneType errors.
"""

import sys
import asyncio
import json
import logging
import argparse
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("youtube_test")

from agents.youtube_utils import (
    process_youtube_content,
    extract_video_id,
    get_transcript,
    validate_youtube_content,
)
from agents.agent import IntrospectAgent


async def test_backup_extraction(url: str) -> Dict[str, Any]:
    """
    Test the backup extraction method

    Args:
        url: YouTube URL to test

    Returns:
        Dictionary with test results
    """
    logger.info(f"Testing backup extraction for {url}")

    # Extract video ID
    video_id = extract_video_id(url)
    logger.info(f"Extracted video ID: {video_id}")

    if not video_id:
        logger.error("Failed to extract video ID")
        return {"error": True, "message": "Failed to extract video ID"}

    # Try to get transcript
    start_time = time.time()
    transcript = get_transcript(url)
    transcript_time = time.time() - start_time

    if transcript:
        logger.info(
            f"Successfully extracted transcript, length: {len(transcript)} chars, time: {transcript_time:.2f}s"
        )
        # Validate transcript content
        is_valid, validation_message = validate_youtube_content(transcript)
        if not is_valid:
            logger.warning(f"Transcript validation failed: {validation_message}")
    else:
        logger.error("Failed to extract transcript")
        return {"error": True, "message": "Failed to extract transcript"}

    # Process YouTube content
    start_time = time.time()
    result = process_youtube_content(url)
    process_time = time.time() - start_time

    if not result["error"]:
        logger.info(f"Successfully processed content in {process_time:.2f}s")
        logger.info(f"Title: {result['video_info'].get('title', 'Unknown')}")
        logger.info(f"Author: {result['video_info'].get('author_name', 'Unknown')}")
        logger.info(f"Content length: {len(result['content'])} characters")
        return result
    else:
        logger.error(f"Failed to process content: {result['message']}")
        return result


async def test_agent_extraction(
    url: str, debug_mode: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Test the agent's extraction method

    Args:
        url: YouTube URL to test
        debug_mode: Whether to enable agent debug mode

    Returns:
        Extracted data or None if failed
    """
    logger.info(f"Testing agent extraction for {url}")

    agent = IntrospectAgent(debug_mode=debug_mode)
    logger.info("Agent initialized, starting extraction...")

    try:
        start_time = time.time()
        result = await agent.extract_key_points_async(url)
        extraction_time = time.time() - start_time

        if not result:
            logger.error("Agent extraction returned None")
            return None

        logger.info(f"Agent extraction completed in {extraction_time:.2f}s")

        # Check for error indicators in the result
        has_error = False
        if "error" in result.get("title", "").lower():
            has_error = True
            logger.warning(f"Error indicated in title: {result.get('title')}")

        # Log the result summary
        logger.info(f"Title: {result.get('title', 'Unknown')}")
        summary = result.get("summary", "No summary")
        logger.info(f"Summary: {summary[:100]}..." if len(summary) > 100 else summary)
        logger.info(f"Insights count: {len(result.get('insights', []))}")

        # Save result to file
        output_path = Path(__file__).parent / "test_output.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        logger.info(f"Saved result to {output_path}")

        return result
    except Exception as e:
        logger.exception(f"Agent extraction failed: {str(e)}")
        return None


async def test_prompt_generation(url: str, debug_mode: bool = True) -> Optional[str]:
    """
    Test the full pipeline including prompt generation

    Args:
        url: YouTube URL to test
        debug_mode: Whether to enable agent debug mode

    Returns:
        Generated prompt or None if failed
    """
    logger.info(f"Testing full pipeline for {url}")

    # Create a test user context
    user_context = {
        "interests": "AI, machine learning, productivity",
        "goals": "Building better applications, improving coding skills",
        "background": "Software developer with Python experience",
    }

    agent = IntrospectAgent(debug_mode=debug_mode)
    logger.info("Agent initialized, starting full pipeline...")

    try:
        start_time = time.time()
        prompt = await agent.process_resource_async(url, user_context)
        total_time = time.time() - start_time

        if not prompt:
            logger.error("Full pipeline returned None")
            return None

        logger.info(f"Full pipeline completed in {total_time:.2f}s")
        logger.info(f"Prompt length: {len(prompt)} chars")
        logger.info(f"Prompt preview: {prompt[:100]}...")

        # Save result to file
        output_path = Path(__file__).parent / "test_prompt_output.md"
        with open(output_path, "w") as f:
            f.write(prompt)
        logger.info(f"Saved prompt to {output_path}")

        return prompt
    except Exception as e:
        logger.exception(f"Full pipeline failed: {str(e)}")
        return None


async def test_event_loop_handling():
    """Test event loop management by creating and running multiple agents"""
    logger.info("Testing event loop management with multiple agents")

    # Create and use multiple agents to test event loop handling
    urls = [
        "https://www.youtube.com/watch?v=d1xFvRD2knU",  # Valid URL
        "https://www.youtube.com/watch?v=invalid_id",  # Invalid URL
    ]

    results = []

    # Create and run multiple agents in sequence to test event loop reuse
    for url in urls:
        agent = IntrospectAgent(debug_mode=True)
        try:
            logger.info(f"Testing URL with new agent: {url}")
            result = await agent.extract_key_points_async(url)
            results.append({"url": url, "success": bool(result), "error": None})
        except Exception as e:
            logger.exception(f"Error processing {url}: {str(e)}")
            results.append({"url": url, "success": False, "error": str(e)})

    # Log results
    logger.info("Event loop handling test results:")
    for result in results:
        status = "✅ Success" if result["success"] else f"❌ Failed: {result['error']}"
        logger.info(f"{result['url']}: {status}")

    return results


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test YouTube transcript extraction")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://www.youtube.com/watch?v=d1xFvRD2knU",
        help="YouTube URL to test",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the full pipeline including prompt generation",
    )
    parser.add_argument(
        "--loop-test", action="store_true", help="Test event loop handling"
    )
    return parser.parse_args()


async def main():
    """Main test function"""
    args = parse_arguments()

    # Set up logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logger.info(f"Testing YouTube URL: {args.url}")

    # Test event loop handling if requested
    if args.loop_test:
        await test_event_loop_handling()
        return

    # Test backup method
    backup_result = await test_backup_extraction(args.url)

    # Test agent method
    agent_result = await test_agent_extraction(args.url)

    # Test full pipeline if requested
    if args.full:
        prompt_result = await test_prompt_generation(args.url)
    else:
        prompt_result = None

    logger.info("\n--- Summary ---")
    if backup_result and not backup_result.get("error"):
        logger.info("✅ Backup extraction: Success")
    else:
        logger.info("❌ Backup extraction: Failed")

    if agent_result and agent_result.get("title"):
        logger.info("✅ Agent extraction: Success")
    else:
        logger.info("❌ Agent extraction: Failed")

    if args.full:
        if prompt_result:
            logger.info("✅ Full pipeline: Success")
        else:
            logger.info("❌ Full pipeline: Failed")


if __name__ == "__main__":
    asyncio.run(main())
