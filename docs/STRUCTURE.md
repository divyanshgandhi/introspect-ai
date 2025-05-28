# Repository Structure & Organization

This document explains the cleaned and organized repository structure for Introspect AI and how it aligns with the Product Requirements Document (PRD) and Engineering Design (ED) specifications.

## Overview

The repository has been reorganized to follow best practices and align with the two-hop design architecture specified in the PRD and the implementation tasks outlined in the ED.

## Directory Structure

### Root Level
```
introspect-ai/
├── README.md                 # Main project overview and quick start
├── dev.sh                    # Development environment setup (ED Task 3.1)
├── deploy.sh                 # Production deployment script (ED Task 3.2)
├── start.sh                  # Container startup script (Docker requirement)
├── environment.example       # Environment configuration template
├── docker-compose.yml        # Development Docker configuration (ED Task 3.2)
├── docker-compose.prod.yml   # Production Docker configuration (ED Task 3.2)
├── Dockerfile               # Main container configuration
├── .dockerignore            # Docker ignore patterns
└── .gitignore               # Git ignore patterns
```

### Documentation (`docs/`)
All documentation is centralized in the `docs/` directory for better organization:

```
docs/
├── README.md                 # Comprehensive documentation
├── prd.md                    # Product Requirements Document
├── ed.md                     # Engineering Design Document
├── DEPLOYMENT.md             # Detailed deployment instructions
├── change-request.md         # Main website integration guide
├── frontend-README.md        # Frontend-specific documentation
├── test_prompt_output.md     # Test output examples
└── STRUCTURE.md             # This file
```

### Scripts (`scripts/`)
Utility scripts are organized in the `scripts/` directory:

```
scripts/
├── test-local.sh            # Local testing script for microservice mode
└── run_test.sh              # Backend API testing script
```

**Note**: Critical scripts remain in root for easy access:
- `dev.sh` - Main development entry point
- `deploy.sh` - Production deployment
- `start.sh` - Required by Docker containers

### Backend (`backend/`)
The backend follows the ED architecture requirements:

```
backend/
├── agents/                  # Agent implementation using Agno framework
├── api/                     # FastAPI application (ED Task 1.1)
│   ├── main.py             # FastAPI app entry point
│   ├── routes.py           # API endpoints (ED Tasks 1.2-1.4)
│   ├── models.py           # Pydantic models for validation (ED Task 1.5)
│   └── __init__.py
├── tests/                   # Unit and integration tests (ED Task 4.1)
│   ├── test_api.py         # API endpoint tests
│   ├── test_youtube.py     # YouTube processing tests
│   └── test_output.json    # Test data
├── infra/                   # Infrastructure configuration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Backend container configuration
├── run_api.py              # API server runner
└── training.json           # Agent training data
```

### Frontend (`frontend/`)
The frontend follows the ED integration requirements:

```
frontend/
├── src/
│   ├── components/         # React components (ED Task 2.2-2.3)
│   ├── lib/
│   │   ├── api.ts         # API client service (ED Task 2.1)
│   │   └── utils.ts       # Utility functions
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── package.json           # Node.js dependencies
├── Dockerfile.prod        # Production container configuration
├── vite.config.ts         # Vite bundler configuration
├── tailwind.config.ts     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

## Alignment with PRD Requirements

### Two-Hop Design Implementation
The structure supports the PRD's two-hop design:

1. **Extract Phase** (`backend/agents/` + `backend/api/routes.py`)
   - Implemented in agent framework
   - Exposed via `/api/extract` endpoint
   - Returns structured JSON as specified in PRD

2. **Personalize Phase** (`backend/agents/` + `backend/api/routes.py`)
   - Implemented in agent framework  
   - Exposed via `/api/personalize` endpoint
   - Generates ChatGPT-ready prompts as specified in PRD

### API Endpoints
The backend API structure implements all PRD requirements:
- `POST /api/extract` - Extract insights from content
- `POST /api/personalize` - Generate personalized prompts
- `POST /api/process` - Combined processing endpoint

## Alignment with ED Tasks

### ✅ Completed ED Tasks
The current structure addresses these ED requirements:

**Backend API Development (ED Section 1)**:
- ✅ 1.1: FastAPI framework set up in `backend/api/`
- ✅ 1.2: Extract endpoint implemented in `backend/api/routes.py`
- ✅ 1.3: Personalize endpoint implemented in `backend/api/routes.py`
- ✅ 1.4: Combined processing endpoint implemented
- ✅ 1.5: Error handling and validation in `backend/api/models.py`

**Frontend Integration (ED Section 2)**:
- ✅ 2.1: API client service in `frontend/src/lib/api.ts`
- ✅ 2.2-2.4: Components updated to use real API
- ✅ 2.5: Result caching implemented

**DevOps & Infrastructure (ED Section 3)**:
- ✅ 3.1: Development environment setup via `dev.sh`
- ✅ 3.2: Docker configuration in place
- ✅ 3.3: Ready for CI/CD pipeline setup

**Testing (ED Section 4)**:
- ✅ 4.1: Backend tests organized in `backend/tests/`
- ✅ 4.2: Frontend test structure in place
- ✅ 4.3: Integration test scripts in `scripts/`

### Microservice Architecture
The structure supports the microservice deployment model:
- Frontend builds to static files (served by nginx)
- Backend runs as containerized FastAPI service
- Both services exposed on different ports (3000, 8000)
- Integration with main website via nginx proxy

## Development Workflow

### Quick Start Commands
```bash
# Development
./dev.sh

# Local testing (production mode)
./scripts/test-local.sh

# Production deployment
./deploy.sh

# Backend testing only
./scripts/run_test.sh
```

### File Organization Benefits

1. **Clear Separation**: Documentation, scripts, and code are clearly separated
2. **Easy Navigation**: Related files are grouped together
3. **Scalability**: Structure supports future growth and additional features
4. **Maintainability**: Clear organization makes maintenance easier
5. **CI/CD Ready**: Structure supports automated testing and deployment

## Next Steps

The organized structure is now ready for:
1. Continued development following ED tasks
2. Implementation of additional features
3. CI/CD pipeline setup
4. Production deployment
5. Integration with main website

All paths and references have been updated to reflect the new structure, ensuring all scripts and documentation work correctly with the reorganized codebase. 