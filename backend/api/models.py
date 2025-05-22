from pydantic import BaseModel
from typing import List, Dict, Optional


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
