from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any, Union
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import the agents module
sys.path.append(str(Path(__file__).parent.parent))
from agents.agent import IntrospectAgent

# Initialize FastAPI app
app = FastAPI(
    title="Introspect AI API",
    description="API for transforming content into personalized ChatGPT prompts",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the IntrospectAgent (shared instance)
introspect_agent = IntrospectAgent()


# Define Pydantic models for request/response validation
class UserContext(BaseModel):
    interests: str = ""
    goals: str = ""
    background: str = ""


class ExtractedData(BaseModel):
    title: str
    summary: str
    insights: List[Dict[str, str]]


class PersonalizeRequest(BaseModel):
    extracted_data: ExtractedData
    user_context: UserContext


class PromptResponse(BaseModel):
    prompt: str


class ProcessResponse(BaseModel):
    extracted_data: ExtractedData
    prompt: str


@app.get("/")
async def root():
    return {"message": "Welcome to Introspect AI API"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Import routes at the end to avoid circular imports
from .routes import router

app.include_router(router)
