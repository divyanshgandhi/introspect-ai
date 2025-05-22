from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any
import json
import io
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools

# Import models from models.py
from .models import (
    UserContext,
    ExtractedData,
    PersonalizeRequest,
    PromptResponse,
    ProcessResponse,
)

# Import introspect_agent from main
from .main import introspect_agent

# Create a thread pool executor
executor = ThreadPoolExecutor()

router = APIRouter(prefix="/api", tags=["introspect"])


# Helper function to run sync functions in a thread
def run_in_threadpool(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))


@router.post("/extract", response_model=ExtractedData)
async def extract_content(
    file: Optional[UploadFile] = File(None), youtube_url: Optional[str] = Form(None)
):
    """
    Extract insights from content (file or YouTube URL).

    Returns structured data with title, summary and key insights.
    """
    if not file and not youtube_url:
        raise HTTPException(
            status_code=400,
            detail="No content provided. Please upload a file or provide a YouTube URL.",
        )

    try:
        # Process based on content type
        if file:
            # Read file content
            file_content = await file.read()
            content = file.filename

            # In a complete implementation, we would process different file types
            # For now, we'll just pass the filename to the agent
        else:
            # Process YouTube URL
            content = youtube_url

        # Run the agent in a separate thread to avoid asyncio issues
        extracted_json = await run_in_threadpool(
            introspect_agent.extract_key_points, content
        )

        # Parse JSON string to dict
        # If extracted_json is already a dict, we don't need to parse it
        if isinstance(extracted_json, dict):
            return extracted_json

        # Otherwise, we assume it's a JSON string
        extracted_data = json.loads(extracted_json)
        return extracted_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting content: {str(e)}"
        )


@router.post("/personalize", response_model=PromptResponse)
async def personalize_content(request: PersonalizeRequest):
    """
    Generate a personalized prompt from extracted insights and user context.
    """
    try:
        # Convert extracted data to dict if it's not already
        if isinstance(request.extracted_data, dict):
            extracted_data = request.extracted_data
        else:
            extracted_data = request.extracted_data.dict()

        # Run the agent in a separate thread to avoid asyncio issues
        prompt = await run_in_threadpool(
            introspect_agent.generate_prompt,
            extracted_data=extracted_data,
            user_context=request.user_context.dict(),
        )

        return {"prompt": prompt}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error personalizing content: {str(e)}"
        )


@router.post("/process", response_model=ProcessResponse)
async def process_content(
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None),
    interests: str = Form(""),
    goals: str = Form(""),
    background: str = Form(""),
):
    """
    Combined endpoint that extracts insights and generates a personalized prompt in one call.
    """
    if not file and not youtube_url:
        raise HTTPException(
            status_code=400,
            detail="No content provided. Please upload a file or provide a YouTube URL.",
        )

    try:
        # Process based on content type
        if file:
            # Read file content
            file_content = await file.read()
            content = file.filename

            # In a complete implementation, we would process different file types
            # For now, we'll just pass the filename to the agent
        else:
            # Process YouTube URL
            content = youtube_url

        # Create user context
        user_context = {
            "interests": interests,
            "goals": goals,
            "background": background,
        }

        # Extract insights using our helper function
        extracted_data = await run_in_threadpool(
            introspect_agent.extract_key_points, content
        )

        # Handle both dict and string cases
        if not isinstance(extracted_data, dict):
            extracted_data = json.loads(extracted_data)

        # Generate prompt using our helper function
        prompt = await run_in_threadpool(
            introspect_agent.generate_prompt,
            extracted_data=extracted_data,
            user_context=user_context,
        )

        return {"extracted_data": extracted_data, "prompt": prompt}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing content: {str(e)}"
        )
