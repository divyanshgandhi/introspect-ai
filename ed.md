# Engineering Design Document: Introspect AI

## Overview

This document outlines the engineering tasks required to integrate the existing backend with the frontend application for Introspect AI - a tool that transforms content from files/links into personalized ChatGPT prompts using a two-hop design.

## Architecture

### Current State

**Backend**:
- Built with Python using the Agno framework
- Two-step agent process:
  1. Extract Agent: Extracts insights from content in structured JSON format
  2. Prompt Agent: Generates personalized ChatGPT prompts from insights

**Frontend**:
- React application with TypeScript
- Components for file upload, YouTube link input, and user context collection
- Mock implementation for content extraction

### Target Architecture

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────┐
│             │     │                      │     │             │
│  Frontend   │────▶│ RESTful API Endpoints│────▶│   Backend   │
│  (React)    │◀────│    (FastAPI/Flask)   │◀────│   (Agno)    │
│             │     │                      │     │             │
└─────────────┘     └──────────────────────┘     └─────────────┘
```

## Engineering Tasks

### 1. Backend API Development

#### 1.1 Create API Framework
- **Task**: Set up a FastAPI/Flask framework for the API endpoints
- **Details**:
  - Install necessary packages (`fastapi`, `uvicorn`, etc.)
  - Create basic app structure in `backend/api/`
  - Configure CORS to allow frontend requests

#### 1.2 Implement Extract Endpoint
- **Task**: Create an endpoint to process content and extract insights
- **Details**:
  - Endpoint: `POST /api/extract`
  - Accept file uploads and YouTube URLs
  - Use existing `IntrospectAgent.extract_key_points()` method
  - Return extracted JSON data

#### 1.3 Implement Personalize Endpoint
- **Task**: Create an endpoint to generate personalized prompts
- **Details**:
  - Endpoint: `POST /api/personalize`
  - Accept extracted insights JSON and user context
  - Use existing `IntrospectAgent.generate_prompt()` method
  - Return formatted prompt text

#### 1.4 Implement Combined Processing Endpoint
- **Task**: Create a convenience endpoint for full processing
- **Details**:
  - Endpoint: `POST /api/process`
  - Accept file/URL and user context
  - Chain both extraction and personalization steps
  - Return final prompt

#### 1.5 Error Handling and Validation
- **Task**: Implement robust error handling and input validation
- **Details**:
  - Validate inputs (file types, URL formats, JSON schemas)
  - Implement appropriate HTTP status codes
  - Return structured error responses

### 2. Frontend Integration

#### 2.1 API Client Service
- **Task**: Create API client service for backend communication
- **Details**:
  - Create `src/lib/api.ts` for API calls
  - Implement fetch methods for all endpoints
  - Add request/response types and error handling

#### 2.2 Update File Upload Component
- **Task**: Enhance FileUpload component to send files to API
- **Details**:
  - Add file format validation
  - Implement file upload to backend API
  - Show upload progress indicators

#### 2.3 Update YouTube Input Component
- **Task**: Enhance YouTubeInput to process URLs via the API
- **Details**:
  - Add URL validation
  - Connect to backend processing endpoint
  - Handle loading states

#### 2.4 Replace Mock Content Processing
- **Task**: Update ContentExtractor to use real API
- **Details**:
  - Replace mock implementation with API calls
  - Implement proper error handling
  - Add loading indicators

#### 2.5 Add Result Caching
- **Task**: Implement caching for processed content
- **Details**:
  - Cache results using React Query
  - Implement cache invalidation strategy
  - Add option to reprocess content

### 3. DevOps & Infrastructure

#### 3.1 Development Environment Setup
- **Task**: Configure development environment
- **Details**:
  - Create a combined dev setup script
  - Configure proxy for local development
  - Document setup process

#### 3.2 Dockerize Application
- **Task**: Create Docker configuration
- **Details**:
  - Create Dockerfile for backend
  - Configure docker-compose for full stack
  - Document Docker usage

#### 3.3 CI/CD Pipeline
- **Task**: Set up CI/CD pipeline
- **Details**:
  - Configure GitHub Actions/similar
  - Set up automated testing
  - Configure deployment process

### 4. Testing

#### 4.1 Backend Unit Tests
- **Task**: Create unit tests for API endpoints
- **Details**:
  - Test all API endpoints
  - Mock agent interactions
  - Test error cases

#### 4.2 Frontend Unit Tests
- **Task**: Create unit tests for frontend components
- **Details**:
  - Test UI components
  - Mock API interactions
  - Test error states

#### 4.3 Integration Tests
- **Task**: Create end-to-end tests
- **Details**:
  - Test full user flows
  - Verify data correctly flows between systems
  - Test edge cases

## API Specifications

### Extract API

```
POST /api/extract
Content-Type: multipart/form-data

Form fields:
- file: (optional) File to process
- youtube_url: (optional) YouTube URL to process

Response:
{
  "title": "Content title",
  "summary": "200-word abstract",
  "insights": [
    { "point": "key takeaway 1", "type": "actionable" },
    { "point": "key takeaway 2", "type": "fact" }
  ]
}
```

### Personalize API

```
POST /api/personalize
Content-Type: application/json

Request:
{
  "extracted_data": {
    "title": "Content title",
    "summary": "200-word abstract",
    "insights": [...]
  },
  "user_context": {
    "interests": "User interests",
    "goals": "User goals",
    "background": "User background"
  }
}

Response:
{
  "prompt": "Generated prompt text..."
}
```

### Process API

```
POST /api/process
Content-Type: multipart/form-data

Form fields:
- file: (optional) File to process
- youtube_url: (optional) YouTube URL to process
- interests: User interests
- goals: User goals
- background: User background

Response:
{
  "extracted_data": {
    "title": "Content title",
    "summary": "200-word abstract",
    "insights": [...]
  },
  "prompt": "Generated prompt text..."
}
```

## Implementation Timeline

### Phase 1: Backend API (Week 1)
- Set up API framework
- Implement endpoints
- Add validation and error handling

### Phase 2: Frontend Integration (Weeks 2-3)
- Create API client service
- Update UI components
- Implement proper loading states

### Phase 3: Testing & Deployment (Week 4)
- Write unit and integration tests
- Set up deployment infrastructure
- Documentation

## Tech Stack

- **Backend**:
  - Python 3.8+
  - FastAPI/Flask
  - Agno framework
  - Pydantic for validation

- **Frontend**:
  - React with TypeScript
  - TanStack Query for data fetching
  - shadcn/ui for UI components
  - Vite for bundling

- **DevOps**:
  - Docker
  - GitHub Actions
  - Pytest for backend testing
  - Vitest for frontend testing

## Next Steps

1. Begin with backend API development
2. Create API client in the frontend
3. Gradually replace mock implementations
4. Implement testing
5. Set up deployment pipeline 